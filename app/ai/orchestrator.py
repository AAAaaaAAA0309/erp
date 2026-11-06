import json
from openai import OpenAI
from ..config import settings
from .tools import TOOL_DEFINITIONS, execute_tool

client = OpenAI(api_key=settings.openai_api_key, base_url=settings.openai_base_url)

# Обратите внимание на правило №4 - мы усилили его
SYSTEM_PROMPT = """Ты — ИИ-ассистент товароучётной системы.
Твоя задача — помогать пользователю управлять товарами, складами и контрагентами.

Правила:
1. Используй инструменты, не выдумывай данные.
2. Если параметров для вызова инструмента недостаточно — задай уточняющий вопрос.
3. После вызова инструмента ответь пользователю на русском.
4. ВАЖНО! При создании контрагента (create_partner) ВСЕГДА сначала вызывай инструмент с параметром confirmed=False. 
   Если инструмент вернет статус "needs_confirmation", перескажи пользователю текст из поля "message" и жди ответа.
   Если пользователь ответит "Да" или "Подтверждаю", ТОЛЬКО ТОГДА вызывай инструмент снова с confirmed=True.
5. Отвечай кратко и по делу.

Текущий пользователь: {username}, роль: {role}."""

def process_message(history, db, user) -> dict:
    # Собираем сообщения для нейросети
    messages = [{"role": "system", "content": SYSTEM_PROMPT.format(username=user.username, role=user.role)}]
    for msg in history:
        messages.append({"role": msg.role, "content": msg.content})
        
    actions = []

    for _ in range(6):
        response = client.chat.completions.create(
            model=settings.openai_model,
            messages=messages,
            tools=TOOL_DEFINITIONS,
            tool_choice="auto",
            temperature=0,
        )
        msg = response.choices[0].message

        if not msg.tool_calls:
            return {"reply": msg.content or "(пустой ответ)", "actions": actions}

        messages.append({
            "role": "assistant",
            "content": msg.content,
            "tool_calls": [
                {"id": tc.id, "type": "function",
                 "function": {"name": tc.function.name, "arguments": tc.function.arguments}}
                for tc in msg.tool_calls
            ],
        })

        for tc in msg.tool_calls:
            try:
                args = json.loads(tc.function.arguments or "{}")
            except json.JSONDecodeError:
                args = {}
            result = execute_tool(tc.function.name, args, db, user)
            actions.append({"tool": tc.function.name, "args": args, "result": result})
            messages.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": json.dumps(result, ensure_ascii=False),
            })

    return {"reply": "Не удалось завершить запрос за разумное число шагов.", "actions": actions}