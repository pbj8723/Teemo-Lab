import dotenv
import requests
import time
import logging
import os
from collections import deque
from sqlalchemy import create_engine, Column, Integer, String, BigInteger
from sqlalchemy.orm import declarative_base, sessionmaker

dotenv.load_dotenv()


# 로그 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

db_ip = os.getenv('DB_IP')
db_port = os.getenv('DB_PORT')
db_username = os.getenv('DB_USERNAME')
db_password = os.getenv('DB_PASSWORD')
db_schema = os.getenv('DB_SCHEMA')

# 데이터베이스 연결 설정
DATABASE_URL = f"mysql+pymysql://{db_username}:{db_password}@{db_ip}:{db_port}/{db_schema}"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()

# 기존 테이블 삭제 및 재생성
# Base.metadata.drop_all(engine)

# 모델 정의
class Summoner(Base):
    __tablename__ = 'summoners'
    id = Column(String(78), primary_key=True)
    accountId = Column(String(56))
    puuid = Column(String(78))
    profileIconId = Column(Integer)
    revisionDate = Column(BigInteger)
    summonerLevel = Column(Integer)
    summonerId = Column(String(78))
    tier = Column(String(30))
    rank = Column(String(5))
    leaguePoints = Column(Integer)
    wins = Column(Integer)
    losses = Column(Integer)

# 테이블 생성
Base.metadata.create_all(engine)

# API 키
API_KEY = os.getenv('RIOT_API_KEY')

# API Rate Limits
MAX_REQUESTS_PER_1_SECOND = 20
MAX_REQUESTS_PER_2_MINUTES = 100

# Queues to keep track of request timestamps
request_times_1_sec = deque(maxlen=MAX_REQUESTS_PER_1_SECOND)
request_times_2_min = deque(maxlen=MAX_REQUESTS_PER_2_MINUTES)

def rate_limit():
    # Check for 1 second limit
    if len(request_times_1_sec) == MAX_REQUESTS_PER_1_SECOND:
        while time.time() - request_times_1_sec[0] < 1:
            time.sleep(0.01)
        request_times_1_sec.popleft()

    # Check for 2 minute limit
    if len(request_times_2_min) == MAX_REQUESTS_PER_2_MINUTES:
        while time.time() - request_times_2_min[0] < 120:
            time.sleep(0.01)
        request_times_2_min.popleft()

    current_time = time.time()
    request_times_1_sec.append(current_time)
    request_times_2_min.append(current_time)

def get_summoner_rank_data(tier, division, page):
    while True:
        rate_limit()
        url = f"https://kr.api.riotgames.com/lol/league-exp/v4/entries/RANKED_SOLO_5x5/{tier}/{division}?page={page}&api_key={API_KEY}"
        response = requests.get(url, verify=False)
        if response.status_code == 429:
            logger.warning("Rate limit exceeded. Retrying in 10 seconds...")
            time.sleep(10)
            continue
        try :
            response.raise_for_status()
        except Exception as e:
            logger.error(f"Error: {e}")
            return None
        logger.info(response.json())
        return response.json()

def get_summoner_data_by_id(summoner_id):
    while True:
        rate_limit()
        url = f"https://kr.api.riotgames.com/lol/summoner/v4/summoners/{summoner_id}?api_key={API_KEY}"
        response = requests.get(url, verify=False)
        if response.status_code == 429:
            logger.warning("Rate limit exceeded. Retrying in 10 seconds...")
            time.sleep(10)
            continue
        try :
            response.raise_for_status()
        except Exception as e:
            logger.error(f"Error: {e}")
            return None
        logger.info(response.json())
        return response.json()

def save_summoner_rank_data(rank_data):
    for entry in rank_data:
        existing_summoner = session.query(Summoner).filter_by(id=entry['summonerId']).first()
        if existing_summoner:
            pass
            # existing_summoner.accountId = summoner_data['accountId']
            # existing_summoner.puuid = summoner_data['puuid']
            # existing_summoner.profileIconId = summoner_data['profileIconId']
            # existing_summoner.revisionDate = summoner_data['revisionDate']
            # existing_summoner.summonerLevel = summoner_data['summonerLevel']
            # existing_summoner.summonerId = entry['summonerId']
            # existing_summoner.tier = entry['tier']
            # existing_summoner.rank = entry['rank']
            # existing_summoner.leaguePoints = entry['leaguePoints']
            # existing_summoner.wins = entry['wins']
            # existing_summoner.losses = entry['losses']
            # logger.info(f"Updated summoner data for {summoner_data['id']}")
        else:
            summoner_data = get_summoner_data_by_id(entry['summonerId'])
            if not summoner_data:
                continue
            new_summoner = Summoner(
                id=summoner_data['id'],
                accountId=summoner_data['accountId'],
                puuid=summoner_data['puuid'],
                profileIconId=summoner_data['profileIconId'],
                revisionDate=summoner_data['revisionDate'],
                summonerLevel=summoner_data['summonerLevel'],
                summonerId=entry['summonerId'],
                tier=entry['tier'],
                rank=entry['rank'],
                leaguePoints=entry['leaguePoints'],
                wins=entry['wins'],
                losses=entry['losses']
            )
            session.add(new_summoner)
            logger.info(f"Added new summoner {summoner_data['id']}")
        session.commit()

# 데이터 수집 및 저장
tiers = ["GOLD", "SILVER", "BRONZE"]
divisions = ["I", "II", "III", "IV"]

for tier in tiers:
    for division in divisions:
        page = 1
        while True:
            logger.info(tier, division, page)
            rank_data = get_summoner_rank_data(tier, division, page)
            if not rank_data:
                break
            save_summoner_rank_data(rank_data)
            session.commit()
            page += 1

logger.info(f"데이터가 저장되었다능.")
