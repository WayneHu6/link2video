import asyncio
import json
import os
import re

from playwright.async_api import async_playwright, expect
import traceback  # For detailed exception logging

from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError

# Path to the cookie file provided by the user
COOKIE_FILE_PATH = "./cookies.txt"


async def load_cookies_from_file(context, cookie_file_path):
    try:
        with open(cookie_file_path, 'r') as f:
            cookies = []
            for line in f:
                if line.startswith('#') or line.strip() == '':
                    continue
                parts = line.strip().split('\t')
                if len(parts) == 7:
                    domain, _, path, secure, expires, name, value = parts
                    cookies.append({
                        "name": name,
                        "value": value,
                        "domain": domain,
                        "path": path,
                        "expires": int(float(expires)) if expires else -1,
                        "httpOnly": False,
                        "secure": secure.lower() == 'true',
                        "sameSite": "Lax"
                    })
            if cookies:
                await context.add_cookies(cookies)
                print(f"Successfully loaded {len(cookies)} cookies from {cookie_file_path}")
            else:
                print(f"No valid cookies found in {cookie_file_path}")
    except FileNotFoundError:
        print(f"Cookie file not found: {cookie_file_path}")
    except Exception as e:
        print(f"Error loading cookies: {e}")


async def attempt_download_method1(page, video_url, filename, referer_url):
    print(f"Attempting download Method 1 (page.request.get): {video_url}")
    try:
        api_response = await page.request.get(
            video_url,
            headers={
                "Referer": referer_url
            },
            timeout=18000
        )
        if api_response.ok:
            video_content = await api_response.body()
            if video_content:
                with open(filename, "wb") as f:
                    f.write(video_content)
                if os.path.exists(filename) and os.path.getsize(filename) > 0:
                    print(f"Method 1: Video downloaded successfully as {filename} (Size: {os.path.getsize(filename)})")
                    return True, filename
                else:
                    print(f"Method 1: File not created or empty after write attempt: {filename}")
                    return False, "Method 1: File not created or empty"
            else:
                print("Method 1: Downloaded video content is empty (api_response.body() was empty).")
                return False, "Method 1: Empty content"
        else:
            error_text = await api_response.text()
            print(f"Method 1: Failed. Status: {api_response.status}, Text: {error_text[:200]}")
            return False, f"Method 1: Status {api_response.status}"
    except Exception as e:
        print(f"Method 1: Error: {type(e).__name__} - {str(e)}")
        traceback.print_exc()
        return False, f"Method 1: Exception {type(e).__name__}"


async def attempt_download_method2(page, video_url, filename):
    print(f"Attempting download Method 2 (page.goto with download event): {video_url}")
    try:
        async with page.expect_download(timeout=180000) as download_info:
            await page.goto(video_url, wait_until="load", timeout=60000)  # Navigate to the video URL itself
        download = await download_info.value
        await download.save_as(filename)
        if os.path.exists(filename) and os.path.getsize(filename) > 0:
            print(f"Method 2: Video downloaded successfully as {filename} (Size: {os.path.getsize(filename)})")
            return True, filename
        else:
            print(f"Method 2: File not created or empty after save_as: {filename}")
            failure_reason = await download.failure()
            if failure_reason:
                print(f"Method 2: Download failure reason: {failure_reason}")
            return False, f"Method 2: File not created or empty (Reason: {failure_reason})"
    except Exception as e:
        print(f"Method 2: Error: {type(e).__name__} - {str(e)}")
        traceback.print_exc()
        return False, f"Method 2: Exception {type(e).__name__}"


async def get_video_url_and_download_playwright(share_url, download_dir):
    video_url_found = None
    video_title = "douyin_video"
    aweme_id = None
    potential_video_items_ref = []
    current_url_page = share_url
    download_status = False
    download_message = "Download process not initiated or failed early."
    final_downloaded_path = None
    os.makedirs(download_dir, exist_ok=True)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36',
            java_script_enabled=True,
            accept_downloads=True
        )

        if os.path.exists(COOKIE_FILE_PATH):
            await load_cookies_from_file(context, COOKIE_FILE_PATH)
        else:
            print(f"Cookie file {COOKIE_FILE_PATH} not found, proceeding without loaded cookies.")

        page = await context.new_page()

        async def intercept_response(response):
            nonlocal potential_video_items_ref
            url = response.url
            status = response.status
            headers = response.headers
            resource_type = response.request.resource_type

            if "video" in resource_type or "media" in resource_type or "mp4" in url:
                if url.endswith(('.mp4',
                                 '.m3u8')) or 'aweme/v1/play' in url or 'playwm' in url or 'playaddr' in url or 'videoflow' in url:
                    if status == 200 or status == 206:
                        print(
                            f"Intercepted direct video-related URL: {url} (Status: {status}, Type: {resource_type}, Content-Type: {headers.get('content-type')})")
                        potential_video_items_ref.append({'url': url, 'type': 'direct_media_url'})

            if 'application/json' in headers.get('content-type', '').lower():
                try:
                    json_body = await response.json()
                    if isinstance(json_body, dict) and json_body.get('aweme_detail'):
                        aweme_detail = json_body['aweme_detail']
                        print("json------")
                        print(aweme_detail)
                        video_data = aweme_detail.get('video', {})
                        for key in ['play_addr', 'download_addr', 'play_addr_h264']:
                            addr_info = video_data.get(key, {})
                            if addr_info.get('url_list'):
                                for video_api_url in addr_info['url_list']:
                                    if video_api_url and video_api_url.startswith("http"):
                                        print(f"Found video URL in JSON ({key}): {video_api_url}")
                                        potential_video_items_ref.append({'url': video_api_url, 'type': f'{key}_json'})
                                        break  # Take first from list
                except Exception as e_json:
                    pass

        page.on("response", lambda res: asyncio.create_task(intercept_response(res)))

        try:
            print(f"Navigating to {share_url}")
            await page.goto(share_url, wait_until="networkidle", timeout=60000)
            current_url_page = page.url
            print(f"Page loaded. Current URL: {current_url_page}")

            match_id = re.search(r"(?:video|vid|aweme_id|modal_id)/([0-9]+)", current_url_page)
            if match_id:
                aweme_id = match_id.group(1)
                video_title = f"douyin_video_{aweme_id}"

            try:
                title_element = await page.query_selector('meta[name="description"]') or await page.query_selector(
                    'meta[property="og:title"]')
                if title_element:
                    content = await title_element.get_attribute('content')
                    if content:
                        video_title_text = re.sub(r'[\/*?"<>|]+', "", content.split('#')[0].split('@')[0].strip()[:50])
                        if video_title_text:
                            video_title = video_title_text if not aweme_id else f"{video_title_text}_{aweme_id}"
            except Exception as e_title:
                print(f"Could not extract title: {e_title}")

            print("Waiting for additional network activity after page load (15s)...")
            await page.wait_for_timeout(15000)

            # Process intercepted URLs
            if potential_video_items_ref:
                seen_urls = {}
                deduplicated_list = [seen_urls.setdefault(item['url'], item) for item in potential_video_items_ref if
                                     item['url'] not in seen_urls]

                def sort_key(item_sort):
                    url_sort, type_sort = item_sort['url'], item_sort['type']
                    if type_sort == 'download_addr_json': return 0
                    if type_sort == 'play_addr_json' and 'playwm' not in url_sort: return 1
                    if type_sort == 'direct_media_url' and url_sort.endswith(
                        '.mp4') and 'playwm' not in url_sort: return 2
                    return 3  # other types

                deduplicated_list.sort(key=sort_key)
                if deduplicated_list:
                    video_url_found = deduplicated_list[0]['url']
                    print(f"Selected video_url_found (type: {deduplicated_list[0]['type']}): {video_url_found}")

            # Fallback: Try to get video src from DOM if network interception fails or yields no good URL
            if not video_url_found:
                print("Network interception did not yield a clear URL, trying DOM video src extraction...")
                video_elements = await page.query_selector_all("video")
                for video_element in video_elements:
                    src = await video_element.get_attribute("src")
                    if src and src.startswith("http") and ".mp4" in src:  # Basic check for MP4
                        print(f"Found video src from DOM: {src}")
                        video_url_found = src
                        break  # Use the first one found
                    elif src and src.startswith("blob:"):
                        print(f"Found blob video src from DOM: {src}. Cannot download directly.")

            if video_url_found:
                if video_url_found.startswith("http://"):
                    video_url_found = video_url_found.replace("http://", "https://", 1)

                safe_video_title = re.sub(r'[^A-Za-z0-9_.-]+', '_', video_title)
                filename = os.path.join(download_dir, f"{safe_video_title}.mp4")

                # Try Method 1
                download_status, msg = await attempt_download_method1(page, video_url_found, filename, current_url_page)
                if download_status:
                    final_downloaded_path = msg
                else:
                    print(f"Method 1 failed: {msg}. Trying Method 2.")
                    # Try Method 2
                    # download_status, msg = await attempt_download_method2(page, video_url_found, filename)
                    if download_status:
                        final_downloaded_path = msg
                    else:
                        print(f"Method 2 failed: {msg}.")

                if download_status:
                    download_message = final_downloaded_path
                else:
                    download_message = "All download methods failed for the selected URL."
                    print(download_message)
            else:
                download_message = "Could not find/select a downloadable video URL after all processing."
                print(download_message)

        except Exception as e_playwright:
            download_message = f"Outer Playwright error: {type(e_playwright).__name__} - {str(e_playwright)}"
            print(f"DEBUG: {download_message}")
            traceback.print_exc()
        finally:
            print("Closing browser.")
            await browser.close()

    return download_status, download_message

from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError
from playwright._impl._errors import TargetClosedError

async def get_aweme_detail(share_url):
    """获取视频的aweme_detail数据"""
    aweme_detail = None
    found_event = asyncio.Event()

    async def intercept_aweme_response(response):
        nonlocal aweme_detail
        try:
            headers = response.headers
            if 'application/json' in headers.get('content-type', '').lower():
                json_body = await response.json()
                if isinstance(json_body, dict) and 'aweme_detail' in json_body:
                    aweme_detail = json_body['aweme_detail']
                    # print("拦截到 aweme_detail 数据：")
                    # print(json.dumps(aweme_detail, indent=2, ensure_ascii=False))
                    found_event.set()  # 标记数据找到
        except Exception as e:
            pass
            # print(f"解析响应失败: {e}")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36',
            java_script_enabled=True
        )

        if os.path.exists(COOKIE_FILE_PATH):
            await load_cookies_from_file(context, COOKIE_FILE_PATH)

        page = await context.new_page()
        page.on("response", intercept_aweme_response)

        async def navigate_and_wait():
            try:
                await page.goto(share_url, wait_until="networkidle", timeout=60000)
            except PlaywrightTimeoutError:
                print("页面加载超时，但可能已获取到 aweme_detail")

        navigation_task = asyncio.create_task(navigate_and_wait())

        try:
            # 等待最多15秒，如果提前拿到数据就退出
            await asyncio.wait_for(found_event.wait(), timeout=15)
            # print("提前检测到 aweme_detail，停止页面加载...")
            pass
        except asyncio.TimeoutError:
            print("等待超时，未从网络响应中获取 aweme_detail")
            # 如果仍未找到，尝试从 script 中提取
            if not aweme_detail:
                print("未从网络拦截中获取到 aweme_detail，尝试从页面脚本中解析...")
                scripts = await page.query_selector_all('script')
                for script in scripts:
                    content = await script.inner_text()
                    if 'aweme_detail' in content:
                        try:
                            json_data = json.loads(content)
                            if json_data.get('aweme_detail'):
                                aweme_detail = json_data['aweme_detail']
                                print("从 script 中提取 aweme_detail 成功：******")
                                break
                        except Exception as e:
                            print(f"解析 script 内容失败: {e}")
                            continue

        finally:
            # 取消导航任务（防止其继续运行并抛出异常）
            if not navigation_task.done():
                navigation_task.cancel()
                try:
                    await navigation_task  # 确保任务取消完成（忽略异常）
                except (asyncio.CancelledError, TargetClosedError):
                    pass  # 忽略取消和关闭异常

            # 关闭资源
            try:
                await page.close()
            except TargetClosedError:
                pass
            try:
                await context.close()
            except TargetClosedError:
                pass
            try:
                await browser.close()
            except TargetClosedError:
                pass

        # print("最终返回的 aweme_detail：****")
        pass
        return aweme_detail




async def main():
    # 0.56 04/09 UyG:/ w@s.re 继《哈利·波特》后，又一部史诗级魔幻大作 # 影视解说 # 美剧推荐 # 奇幻电影 # 感人电影  https://v.douyin.com/CXnUwSNliW4/ 复制此链接，打开Dou音搜索，直接观看视频！
    sample_share_url = "https://v.douyin.com/CXnUwSNliW4/"
    download_dir = "./Downloaded/douyin_videos_playwright"

    print(f"Processing share URL with Playwright: {sample_share_url}")
    success = False
    message = "Main function did not complete as expected."
    try:
        success, message = await get_video_url_and_download_playwright(sample_share_url, download_dir)
        if success:
            print(f"Playwright Download successful: {message}")
            # Verify file exists as a final check from main
            if os.path.exists(message) and os.path.getsize(message) > 0:
                print(f"CONFIRMED: Video file exists and is not empty: {message}")
            else:
                print(f"ERROR: Main function reported success, but file is missing or empty: {message}")
                success = False  # Correct status
                message = f"File missing/empty: {message}"
        else:
            print(f"Playwright Download failed: {message}")
    except Exception as e_main:
        print(f"Critical error in main: {type(e_main).__name__} - {str(e_main)}")
        traceback.print_exc()
        message = f"Critical error in main: {str(e_main)}"

    # Final check of download directory
    if success:
        print(f"Script finished. Downloaded video should be at: {message}")
    else:
        print(f"Script finished. Download failed. Last error: {message}")
        print(f"Checking contents of {download_dir}:")
        if os.path.exists(download_dir):
            files = os.listdir(download_dir)
            if files:
                for f_item in files:
                    print(f" - {f_item} (Size: {os.path.getsize(os.path.join(download_dir, f_item))})")
            else:
                print(" (Directory is empty)")
        else:
            print(" (Directory does not exist)")


if __name__ == "__main__":
    asyncio.run(main())

