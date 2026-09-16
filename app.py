import os

from flask import Flask, jsonify, request
from flask_cors import CORS
from groq import Groq


app = Flask(__name__)


# ============================================================
# 환경변수
# ============================================================

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise RuntimeError("GROQ_API_KEY 환경변수가 설정되지 않았습니다.")


# GitHub Pages 주소의 도메인 부분만 입력
# 예: https://cheaweon.github.io
allowed_origins = os.environ.get(
    "ALLOWED_ORIGINS",
    "http://127.0.0.1:5500,http://localhost:5500"
).split(",")


CORS(
    app,
    resources={
        r"/api/*": {
            "origins": allowed_origins
        }
    }
)


client = Groq(api_key=GROQ_API_KEY)


# ============================================================
# Re:Body 전시 안내 기준 문서
# ============================================================

SYSTEM_PROMPT = """
당신은 Re:Body(리:보디) 졸업작품 전시 안내 챗봇입니다.

다음 프로젝트 정보를 기준으로 관람객과 평가자의 질문에
정확하고 이해하기 쉽게 답변하세요.

[프로젝트 기본 정보]

프로젝트명: Re:Body(리:보디)

한 줄 소개:
내 몸을 재구성해주는 지능형 건강관리 솔루션

개발팀:
경남대학교 컴퓨터공학부 맥앤치즈 팀

프로젝트 목적:
식단, 활동량, 수면, 수분 데이터를 통합하여 사용자의
생활습관을 종합적으로 확인하고 개인 맞춤형 건강관리를
지원하는 서비스입니다.

[핵심 기능]

1. AI 음식 분석
사용자가 촬영한 음식 사진에서 음식을 인식하고
음식 종류와 영양정보를 분석합니다.

2. 식단 기록
AI가 분석한 음식과 영양정보를 사용자의 식단 기록으로
저장할 수 있습니다.

3. 활동량 관리
Google Fit과 연동하여 걸음 수, 활동량, 소모 칼로리 등의
데이터를 확인합니다.

4. 수면 및 수분 기록
사용자가 수면시간과 수분 섭취량을 기록하고 확인할 수 있습니다.

5. 캘린더
날짜별 식단, 활동, 수면 등의 건강 기록을 한 화면에서 확인합니다.

6. 그래프
일정 기간 동안 축적된 건강 데이터의 변화와 패턴을
그래프로 확인합니다.

7. 종합 피드백
식단, 활동량, 수면, 수분 데이터를 함께 분석하여
사용자의 생활습관과 목표에 맞는 건강관리 정보를 제공합니다.

8. AI 챗봇
사용자가 기록한 건강 데이터를 바탕으로 건강관리와 관련된
질문에 답변하도록 설계했습니다.

[AI 및 개발 기술]

프론트엔드:
Flutter, Dart

백엔드:
Python, Flask

데이터베이스:
MySQL

외부 연동:
Google Fit

음식 객체 탐지:
YOLOv10n

음식 분류:
YOLOv8m-cls

챗봇:
Groq API 기반 LLM

[음식 AI 처리 과정]

음식 사진 촬영
→ YOLOv10n 객체 탐지
→ 음식 영역 자르기
→ YOLOv8m-cls 음식 분류
→ 영양정보 분석
→ 사용자 식단 기록

[프로젝트 차별점]

단순히 음식이나 운동만 기록하는 서비스가 아닙니다.

음식 AI를 이용해 식단 입력의 번거로움을 줄이고,
식단, 활동, 수면, 수분 데이터를 하나의 건강관리 흐름으로
연결한 것이 특징입니다.

캘린더와 그래프를 이용해 누적 기록과 생활 패턴을 확인하고,
종합 피드백과 AI 챗봇을 통해 사용자의 데이터에 기반한
건강관리 정보를 제공하도록 설계했습니다.

[답변 원칙]

- 답변은 한국어로 작성합니다.
- 전시 관람객이 이해하기 쉽게 3~6문장 정도로 답변합니다.
- 프로젝트에 실제로 구현되거나 설계된 내용만 설명합니다.
- 확인되지 않은 정확도나 성능 수치를 임의로 만들지 않습니다.
- 의학적 진단이나 치료를 제공한다고 말하지 않습니다.
- 정의되지 않은 기능에 대해서는 임의로 생성하지 않습니다.
- 모르는 내용은 "해당 내용은 맥앤치즈 팀장에게 문의해 주세요."
  라고 답변합니다.
"""


# ============================================================
# 서버 상태 확인
# ============================================================

@app.get("/")
def home():
    return jsonify({
        "status": "ok",
        "message": "Re:Body chatbot server is running."
    })


@app.get("/api/health")
def health():
    return jsonify({
        "status": "ok"
    })


# ============================================================
# 전시 안내 챗봇 API
# ============================================================

@app.post("/api/exhibition-chat")
def exhibition_chat():
    data = request.get_json(silent=True) or {}

    message = str(data.get("message", "")).strip()

    if not message:
        return jsonify({
            "error": "질문을 입력해 주세요."
        }), 400

    if len(message) > 300:
        return jsonify({
            "error": "질문은 300자 이하로 입력해 주세요."
        }), 400

    try:
        completion = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT
                },
                {
                    "role": "user",
                    "content": message
                }
            ],
            temperature=0.2,
            max_tokens=700
        )

        answer = completion.choices[0].message.content

        return jsonify({
            "answer": answer
        })

    except Exception as error:
        app.logger.exception("Groq API 요청 실패: %s", error)

        return jsonify({
            "error": "현재 AI 답변을 불러오지 못했습니다. 잠시 후 다시 시도해 주세요."
        }), 500


# ============================================================
# 로컬 실행
# ============================================================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))

    app.run(
        host="0.0.0.0",
        port=port,
        debug=False
    )