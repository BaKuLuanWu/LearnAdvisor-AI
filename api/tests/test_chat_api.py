import requests
import json

# 你的FastAPI服务地址
BASE_URL = "http://localhost:8000"


def test_create_conv_api():
    test_data1 = {
        "user_id": "019bf364-e196-71cd-9522-e0f49d773f7d",
        "title": "测试对话3",
    }
    ENDPOINT1 = f"{BASE_URL}/create/conversation"
    try:
        print(f"正在测试接口: {ENDPOINT1}")
        print(f"发送数据: {json.dumps(test_data1, ensure_ascii=False)}")

        response = requests.post(ENDPOINT1, json=test_data1)

        print(f"状态码: {response.status_code}")
        print(f"响应内容: {response.text}")

        if response.status_code == 200:
            print("✅ 接口调用成功！")
            result = response.json()
            if result.get("code") == 200:
                print(f"✅ 创建的对话ID: {result.get('data')}")
            else:
                print(f"⚠️ 业务逻辑错误: {result}")
        else:
            print(f"❌ 接口调用失败")

    except requests.exceptions.ConnectionError:
        print(f"❌ 无法连接到服务，请确保FastAPI服务正在运行: {BASE_URL}")
    except Exception as e:
        print(f"❌ 发生错误: {e}")


def test_chat_api():
    test_data2 = {
        "user_id": "019bf364-e196-71cd-9522-e0f49d773f7d",
        "conv_id": "0699d260-ba21-7bba-8000-26e83cbde0df",
        "user_input": "上一句说了啥",
    }
    ENDPOINT2 = f"{BASE_URL}/chat"
    try:
        print(f"正在测试接口: {ENDPOINT2}")
        print(f"发送数据: {json.dumps(test_data2, ensure_ascii=False)}")

        response = requests.post(ENDPOINT2, json=test_data2)

        print(f"状态码: {response.status_code}")
        print(f"响应内容: {response.text}")

        if response.status_code == 200:
            print("✅ 接口调用成功！")
            result = response.json()
            if result.get("code") == 200:
                print(f"✅ 创建的对话ID: {result.get('data')}")
            else:
                print(f"⚠️ 业务逻辑错误: {result}")
        else:
            print(f"❌ 接口调用失败")

    except requests.exceptions.ConnectionError:
        print(f"❌ 无法连接到服务，请确保FastAPI服务正在运行: {BASE_URL}")
    except Exception as e:
        print(f"❌ 发生错误: {e}")


def test_get_conv_detail_api():
    test_data3 = "0698961a-78d4-7938-8000-c502de970d5c"
    ENDPOINT3 = f"{BASE_URL}/get/conversation/{test_data3}"
    try:
        print(f"正在测试接口: {ENDPOINT3}")

        response = requests.get(ENDPOINT3)

        print(f"状态码: {response.status_code}")
        print(f"响应内容: {response.text}")

        if response.status_code == 200:
            print("✅ 接口调用成功！")
            result = response.json()
            if result.get("code") == 200:
                print(f"✅ 创建的对话ID: {result.get('data')}")
            else:
                print(f"⚠️ 业务逻辑错误: {result}")
        else:
            print(f"❌ 接口调用失败")

    except requests.exceptions.ConnectionError:
        print(f"❌ 无法连接到服务，请确保FastAPI服务正在运行: {BASE_URL}")
    except Exception as e:
        print(f"❌ 发生错误: {e}")


def test_get_conv_list_api():
    test_data4 = "019bf364-e196-71cd-9522-e0f49d773f7d"
    ENDPOINT4 = f"{BASE_URL}/get/conversation/list/{test_data4}"
    try:
        print(f"正在测试接口: {ENDPOINT4}")

        response = requests.get(ENDPOINT4)

        print(f"状态码: {response.status_code}")
        print(f"响应内容: {response.text}")

        if response.status_code == 200:
            print("✅ 接口调用成功！")
            result = response.json()
            if result.get("code") == 200:
                print(f"✅ 创建的对话ID: {result.get('data')}")
            else:
                print(f"⚠️ 业务逻辑错误: {result}")
        else:
            print(f"❌ 接口调用失败")

    except requests.exceptions.ConnectionError:
        print(f"❌ 无法连接到服务，请确保FastAPI服务正在运行: {BASE_URL}")
    except Exception as e:
        print(f"❌ 发生错误: {e}")


def test_clear_intent_vector_store_api():
    ENDPOINT5 = f"{BASE_URL}/clear-intent-vector-store"
    try:
        print(f"正在测试接口: {ENDPOINT5}")

        response = requests.post(ENDPOINT5)

        print(f"状态码: {response.status_code}")
        print(f"响应内容: {response.text}")

        if response.status_code == 200:
            print("✅ 接口调用成功！")
            result = response.json()
            if result.get("code") == 200:
                print(f"✅ 创建的对话ID: {result.get('data')}")
            else:
                print(f"⚠️ 业务逻辑错误: {result}")
        else:
            print(f"❌ 接口调用失败")

    except requests.exceptions.ConnectionError:
        print(f"❌ 无法连接到服务，请确保FastAPI服务正在运行: {BASE_URL}")
    except Exception as e:
        print(f"❌ 发生错误: {e}")



if __name__ == "__main__":
    test_chat_api()
    # test_clear_intent_vector_store_api()
    # test_get_conv_list_api()
