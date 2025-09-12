import redis
import asyncio
import json
import os
from datetime import datetime
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

def test_redis_sync():
    """동기 Redis 연결 테스트"""
    try:
        # Redis 클라이언트 생성 (.env에서 설정 로드)
        r = redis.Redis(
            host=os.getenv('REDIS_HOST', 'localhost'),
            port=int(os.getenv('REDIS_PORT', 6379)),
            db=int(os.getenv('REDIS_DB', 0)),
            password=os.getenv('REDIS_PASSWORD'),
            decode_responses=True
        )
        
        # 연결 테스트
        r.ping()
        print("✅ Redis 동기 연결 성공!")
        
        # 기본 SET/GET 테스트
        r.set('test_key', 'test_value')
        value = r.get('test_key')
        print(f"✅ SET/GET 테스트 성공: {value}")
        
        # JSON 데이터 저장/조회 테스트
        test_data = {
            'session_id': 'test_session_123',
            'messages': [
                {'role': 'user', 'content': '안녕하세요', 'timestamp': str(datetime.now())},
                {'role': 'assistant', 'content': '안녕하세요! 오늘 기분은 어떠세요?', 'timestamp': str(datetime.now())}
            ]
        }
        r.set('chat:test_session_123', json.dumps(test_data, ensure_ascii=False))
        stored_data = json.loads(r.get('chat:test_session_123'))
        print(f"✅ JSON 저장/조회 테스트 성공: {len(stored_data['messages'])}개 메시지")
        
        # 리스트 데이터 테스트
        r.lpush('chat_history:test_session', '첫번째 메시지')
        r.lpush('chat_history:test_session', '두번째 메시지')
        messages = r.lrange('chat_history:test_session', 0, -1)
        print(f"✅ 리스트 테스트 성공: {messages}")
        
        # 정리
        r.delete('test_key', 'chat:test_session_123', 'chat_history:test_session')
        print("✅ 테스트 데이터 정리 완료")
        
        return True
        
    except Exception as e:
        print(f"❌ Redis 동기 연결 실패: {e}")
        return False

async def test_redis_async():
    """비동기 Redis 연결 테스트"""
    try:
        # redis-py 5.0+에서는 비동기도 지원 (.env에서 설정 로드)
        r = redis.asyncio.Redis(
            host=os.getenv('REDIS_HOST', 'localhost'),
            port=int(os.getenv('REDIS_PORT', 6379)),
            db=int(os.getenv('REDIS_DB', 0)),
            password=os.getenv('REDIS_PASSWORD'),
            decode_responses=True
        )
        
        # 연결 테스트
        await r.ping()
        print("✅ Redis 비동기 연결 성공!")
        
        # 비동기 SET/GET 테스트
        await r.set('async_test_key', 'async_test_value')
        value = await r.get('async_test_key')
        print(f"✅ 비동기 SET/GET 테스트 성공: {value}")
        
        # 채팅 메시지 시뮬레이션
        session_id = "async_session_123"
        chat_key = f"chat_messages:{session_id}"
        
        # 메시지 추가
        messages = [
            {'role': 'user', 'content': '안녕하세요', 'timestamp': str(datetime.now())},
            {'role': 'assistant', 'content': '안녕하세요! 무엇을 도와드릴까요?', 'timestamp': str(datetime.now())},
            {'role': 'user', 'content': '오늘 기분이 좋아요', 'timestamp': str(datetime.now())}
        ]
        
        for msg in messages:
            await r.lpush(chat_key, json.dumps(msg, ensure_ascii=False))
        
        # 메시지 조회 (최근 10개)
        stored_messages = await r.lrange(chat_key, 0, 9)
        stored_messages.reverse()  # 시간순 정렬
        
        print(f"✅ 채팅 메시지 저장/조회 성공: {len(stored_messages)}개 메시지")
        for i, msg in enumerate(stored_messages):
            parsed_msg = json.loads(msg)
            print(f"   {i+1}. [{parsed_msg['role']}]: {parsed_msg['content']}")
        
        # TTL 설정 테스트 (24시간)
        await r.expire(chat_key, 86400)
        ttl = await r.ttl(chat_key)
        print(f"✅ TTL 설정 성공: {ttl}초 남음")
        
        # 정리
        await r.delete('async_test_key', chat_key)
        await r.aclose()
        print("✅ 비동기 테스트 데이터 정리 완료")
        
        return True
        
    except Exception as e:
        print(f"❌ Redis 비동기 연결 실패: {e}")
        return False

def test_chat_flow_simulation():
    """채팅 플로우 시뮬레이션 테스트"""
    try:
        r = redis.Redis(
            host=os.getenv('REDIS_HOST', 'localhost'),
            port=int(os.getenv('REDIS_PORT', 6379)),
            db=int(os.getenv('REDIS_DB', 0)),
            password=os.getenv('REDIS_PASSWORD'),
            decode_responses=True
        )
        r.ping()
        
        session_id = "flow_test_session"
        
        # 1단계: 기분 확인
        mood_data = {
            'session_id': session_id,
            'current_step': 'mood_check',
            'user_mood': 'happy',
            'messages': [
                {'role': 'assistant', 'content': '안녕하세요! 오늘 기분은 어떠세요?'},
                {'role': 'user', 'content': '오늘 기분이 정말 좋아요!'}
            ]
        }
        r.set(f"chat_state:{session_id}", json.dumps(mood_data, ensure_ascii=False))
        
        # 2단계: 취미 확인
        hobby_data = {
            'session_id': session_id,
            'current_step': 'hobby_check',
            'user_mood': 'happy',
            'previous_hobby': 'reading',
            'current_hobby': 'gaming',
            'hobby_changed': True,
            'messages': mood_data['messages'] + [
                {'role': 'assistant', 'content': '요즘 어떤 취미활동을 하고 계세요?'},
                {'role': 'user', 'content': '요즘 게임하는 재미에 빠져있어요!'}
            ]
        }
        r.set(f"chat_state:{session_id}", json.dumps(hobby_data, ensure_ascii=False))
        
        # 3단계: 상품 추천 준비
        recommend_data = {
            'session_id': session_id,
            'current_step': 'recommendation_ready',
            'user_mood': 'happy',
            'current_hobby': 'gaming',
            'should_update_hobby': True,
            'ready_for_recommendation': True
        }
        r.set(f"chat_state:{session_id}", json.dumps(recommend_data, ensure_ascii=False))
        
        # 상태 조회 테스트
        final_state = json.loads(r.get(f"chat_state:{session_id}"))
        print("✅ 채팅 플로우 시뮬레이션 성공!")
        print(f"   현재 단계: {final_state['current_step']}")
        print(f"   사용자 기분: {final_state['user_mood']}")
        print(f"   현재 취미: {final_state['current_hobby']}")
        print(f"   취미 업데이트 필요: {final_state['should_update_hobby']}")
        
        # 정리
        r.delete(f"chat_state:{session_id}")
        return True
        
    except Exception as e:
        print(f"❌ 채팅 플로우 테스트 실패: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Redis 연결 테스트 시작...")
    print("\n" + "="*50)
    
    # 동기 테스트
    print("📋 1. 동기 Redis 테스트")
    sync_result = test_redis_sync()
    
    print("\n" + "="*50)
    
    # 비동기 테스트
    print("📋 2. 비동기 Redis 테스트")
    async_result = asyncio.run(test_redis_async())
    
    print("\n" + "="*50)
    
    # 채팅 플로우 테스트
    print("📋 3. 채팅 플로우 시뮬레이션 테스트")
    flow_result = test_chat_flow_simulation()
    
    print("\n" + "="*50)
    print("📊 테스트 결과 요약:")
    print(f"   동기 연결: {'✅ 성공' if sync_result else '❌ 실패'}")
    print(f"   비동기 연결: {'✅ 성공' if async_result else '❌ 실패'}")
    print(f"   채팅 플로우: {'✅ 성공' if flow_result else '❌ 실패'}")
    
    if all([sync_result, async_result, flow_result]):
        print("\n🎉 모든 테스트 통과! Redis 연동 준비 완료!")
    else:
        print("\n⚠️  일부 테스트 실패. Redis 서버 상태를 확인해주세요.")