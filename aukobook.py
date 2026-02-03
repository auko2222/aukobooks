import os
import sys
import time
import random
import requests
import getpass
import json
import hashlib
import datetime
from bs4 import BeautifulSoup as bs
import urllib.parse

# Stealth mode - adds realistic delays
STEALTH_MODE = False

# Terminal colors
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_banner():
    banner = f"""
{Colors.HEADER}{Colors.BOLD}
    ╔═══════════════════════════════════════════════════════════════════════╗
    ║                                                                       ║
    ║   █████╗ ██╗   ██╗██╗  ██╗ ██████╗ ██████╗  ██████╗  ██████╗ ██╗  ██╗ ║
    ║  ██╔══██╗██║   ██║██║ ██╔╝██╔═══██╗██╔══██╗██╔═══██╗██╔═══██╗██║ ██╔╝ ║
    ║  ███████║██║   ██║█████╔╝ ██║   ██║██████╔╝██║   ██║██║   ██║█████╔╝  ║
    ║  ██╔══██║██║   ██║██╔═██╗ ██║   ██║██╔══██╗██║   ██║██║   ██║██╔═██╗  ║
    ║  ██║  ██║╚██████╔╝██║  ██╗╚██████╔╝██████╔╝╚██████╔╝╚██████╔╝██║  ██╗ ║
    ║  ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚═════╝  ╚═════╝  ╚═════╝ ╚═╝  ╚═╝ ║
    ║                                                                       ║
    ║                    {Colors.YELLOW}━━━ for educational use ━━━{Colors.HEADER}                        ║
    ║                                                                       ║
    ╚═══════════════════════════════════════════════════════════════════════╝
{Colors.ENDC}"""
    print(banner)

def print_box(title, items, selected=None):
    """Print a nice box with items"""
    width = 60
    print(f"\n{Colors.CYAN}    ╔{'═' * width}╗{Colors.ENDC}")
    print(f"{Colors.CYAN}    ║{Colors.BOLD}{Colors.YELLOW} {title.center(width-1)}{Colors.ENDC}{Colors.CYAN}║{Colors.ENDC}")
    print(f"{Colors.CYAN}    ╠{'═' * width}╣{Colors.ENDC}")

    for i, item in enumerate(items):
        marker = f"{Colors.GREEN}►{Colors.ENDC}" if i == selected else " "
        num = f"{Colors.BOLD}[{i+1}]{Colors.ENDC}"
        text = item[:width-10] if len(item) > width-10 else item
        padding = width - len(text) - 8
        print(f"{Colors.CYAN}    ║{Colors.ENDC} {marker} {num} {text}{' ' * padding}{Colors.CYAN}║{Colors.ENDC}")

    print(f"{Colors.CYAN}    ╚{'═' * width}╝{Colors.ENDC}")

def print_menu(options):
    """Print menu options"""
    print(f"\n{Colors.DIM}    ─────────────────────────────────────{Colors.ENDC}")
    for key, desc in options.items():
        print(f"    {Colors.BOLD}{Colors.YELLOW}[{key}]{Colors.ENDC} {desc}")
    print(f"{Colors.DIM}    ─────────────────────────────────────{Colors.ENDC}")

def print_progress(current, total, activity_name, status="working"):
    """Print a progress bar"""
    bar_width = 30
    progress = current / total if total > 0 else 1
    filled = int(bar_width * progress)
    bar = f"{'█' * filled}{'░' * (bar_width - filled)}"

    if status == "success":
        color = Colors.GREEN
        symbol = "✓"
    elif status == "fail":
        color = Colors.RED
        symbol = "✗"
    else:
        color = Colors.CYAN
        symbol = "●"

    print(f"\r    {color}{symbol}{Colors.ENDC} [{bar}] {current}/{total} - {activity_name[:30]}", end="", flush=True)

def print_status(message, status="info"):
    """Print a status message"""
    if status == "success":
        print(f"    {Colors.GREEN}✓ {message}{Colors.ENDC}")
    elif status == "error":
        print(f"    {Colors.RED}✗ {message}{Colors.ENDC}")
    elif status == "warning":
        print(f"    {Colors.YELLOW}! {message}{Colors.ENDC}")
    else:
        print(f"    {Colors.CYAN}● {message}{Colors.ENDC}")

# Global session to maintain cookies
session = requests.Session()

def stealth_delay(delay_type="activity"):
    """Add realistic random delays when legit mode mode is on"""
    global STEALTH_MODE
    if not STEALTH_MODE:
        return

    if delay_type == "part":
        # Delay between parts of same activity (2-5 seconds - reading/thinking)
        delay = random.uniform(2, 5)
    elif delay_type == "activity":
        # Delay between activities (5-15 seconds - like completing a question)
        delay = random.uniform(5, 15)
    elif delay_type == "section":
        # Delay between sections (15-45 seconds - taking a break)
        delay = random.uniform(15, 45)
    else:
        delay = random.uniform(3, 8)

    # Show countdown
    print(f"{Colors.DIM}    ⏳ Waiting {delay:.1f}s...{Colors.ENDC}", end="", flush=True)
    time.sleep(delay)
    print(f"\r{' ' * 40}\r", end="", flush=True)  # Clear the line

def checksum(activity_id, ts, token, buildkey, part, complete):
    path = f'content_resource/{activity_id}/activity'
    data = f'{path}{ts}{token}{activity_id}{part}{complete}{buildkey}'
    md5 = hashlib.md5()
    md5.update(data.encode('utf-8'))
    return md5.hexdigest()

def get_buildkey():
    res = session.get('https://learn.zybooks.com')
    soup = bs(res.text, features='lxml')
    app_json = soup.find('meta', attrs={'name': 'zybooks-web/config/environment'})
    if not app_json:
        raise Exception('Could not find buildkey')
    return json.loads(urllib.parse.unquote(app_json['content']))['APP']['BUILDKEY']

def login(email, password):
    url = 'https://zyserver.zybooks.com/v1/signin'
    data = {'email': email, 'password': password}
    r = session.post(url=url, json=data)
    response = r.json()

    if not response.get('success'):
        return None

    token = response['session']['auth_token']
    session.headers.update({'Authorization': f'Bearer {token}'})
    return response

def get_books(token, user_id):
    url = f'https://zyserver.zybooks.com/v1/user/{user_id}/items?items=%5B%22zybooks%22%5D'
    r = session.get(url)
    response = r.json()
    if not response.get('success'):
        return []
    return response.get('items', {}).get('zybooks', [])

def get_chapters(token, zybook_code):
    url = f'https://zyserver.zybooks.com/v1/zybooks?zybooks=%5B%22{zybook_code}%22%5D'
    r = session.get(url)
    response = r.json()
    if not response.get('success'):
        return []
    return response.get('zybooks', [])

def get_problems(token, zybook_code, chapter_number, section_number):
    url = f'https://zyserver.zybooks.com/v1/zybook/{zybook_code}/chapter/{chapter_number}/section/{section_number}'
    r = session.get(url)
    return r.json()

def solve_problem(token, zybook_code, problem, buildkey):
    activity_id = problem['id']
    activity_type = problem['type']

    if activity_type == 'html':
        return True, "Skipped (HTML content)"

    url = f'https://zyserver.zybooks.com/v1/content_resource/{activity_id}/activity'
    headers = {
        'Origin': 'https://learn.zybooks.com',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Content-Type': 'application/json',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
    }

    now = datetime.datetime.now(datetime.timezone.utc)
    timestamp = now.strftime("%Y-%m-%dT%H:%M:%S.") + f"{now.microsecond // 1000:03d}Z"
    metadata = {"nextClicked": True, "nextLevel": False, "computerTime": timestamp}

    parts = problem['parts']
    success_count = 0
    total_parts = max(1, parts)

    if parts == 0:
        data = {
            "part": 0, "complete": 1, "metadata": metadata,
            "zybook_code": zybook_code, "timestamp": timestamp,
            "__cs__": checksum(activity_id, timestamp, token, buildkey, 0, 1)
        }
        r = session.post(url=url, json=data, headers=headers)
        if r.json().get('success'):
            success_count += 1
        time.sleep(0.05)
    else:
        for part_num in range(parts):
            # Regenerate timestamp for each part in stealth mode
            if STEALTH_MODE:
                now = datetime.datetime.now(datetime.timezone.utc)
                timestamp = now.strftime("%Y-%m-%dT%H:%M:%S.") + f"{now.microsecond // 1000:03d}Z"
                metadata = {"nextClicked": True, "nextLevel": False, "computerTime": timestamp}

            data = {
                "part": part_num, "complete": 1, "metadata": metadata,
                "zybook_code": zybook_code, "timestamp": timestamp,
                "__cs__": checksum(activity_id, timestamp, token, buildkey, part_num, 1)
            }
            r = session.post(url=url, json=data, headers=headers)
            if r.json().get('success'):
                success_count += 1

            if STEALTH_MODE and part_num < parts - 1:
                stealth_delay("part")
            else:
                time.sleep(0.05)

    if success_count == total_parts:
        return True, f"Completed ({success_count}/{total_parts} parts)"
    else:
        return False, f"Partial ({success_count}/{total_parts} parts)"

def is_subscription_active(book):
    """Check if subscription is still active"""
    end_date = book.get('subscription_end_date') or book.get('end_date')
    if end_date:
        try:
            end_dt = datetime.datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            if end_dt < datetime.datetime.now(datetime.timezone.utc):
                return False
        except:
            pass
    return book.get('user_subscribed', True)

def run_completion(token, zybook_code, buildkey, chapters_data, selected_chapters=None, selected_sections=None):
    """Run the completion process"""
    global STEALTH_MODE
    clear_screen()
    print_banner()

    mode_text = f"{Colors.YELLOW}LEGIT MODE{Colors.ENDC}" if STEALTH_MODE else f"{Colors.CYAN}FAST MODE{Colors.ENDC}"
    print(f"\n{Colors.BOLD}{Colors.GREEN}    ━━━ STARTING AUTO-COMPLETE ━━━{Colors.ENDC} [{mode_text}]\n")

    if STEALTH_MODE:
        print(f"{Colors.YELLOW}    ⚠ legit mode ON - adding realistic delays while completing activities{Colors.ENDC}\n")

    total_activities = 0
    completed_activities = 0
    failed_activities = 0

    for term in chapters_data:
        for chapter in term['chapters']:
            chapter_num = chapter['number']

            # Skip if not selected
            if selected_chapters and chapter_num not in selected_chapters:
                continue

            chapter_title = chapter.get('title', f'Chapter {chapter_num}')
            print(f"\n{Colors.BOLD}{Colors.CYAN}    ╔══ Chapter {chapter_num}: {chapter_title[:40]}{Colors.ENDC}")

            for section in chapter['sections']:
                section_num = section['number']

                # Skip if not selected
                if selected_sections and (chapter_num, section_num) not in selected_sections:
                    continue

                section_title = section.get('title', f'Section {section_num}')
                print(f"{Colors.CYAN}    ╠─ Section {chapter_num}.{section_num}: {section_title[:35]}{Colors.ENDC}")

                try:
                    problems = get_problems(token, zybook_code, chapter_num, section_num)
                    activities = problems.get('section', {}).get('content_resources', [])

                    for i, problem in enumerate(activities):
                        activity_type = problem.get('type', 'unknown')
                        activity_name = problem.get('title') or problem.get('name') or f'{activity_type}'

                        if activity_type == 'html':
                            continue

                        total_activities += 1
                        success, msg = solve_problem(token, zybook_code, problem, buildkey)

                        if success:
                            completed_activities += 1
                            print(f"{Colors.GREEN}    ║   ✓ {activity_type}: complete{Colors.ENDC}")
                        else:
                            failed_activities += 1
                            print(f"{Colors.RED}    ║   ✗ {activity_type}: {activity_name[:30]}{Colors.ENDC}")

                        # Stealth delay between activities
                        stealth_delay("activity")

                except Exception as e:
                    print(f"{Colors.RED}    ║   Error: {str(e)[:40]}{Colors.ENDC}")

                # Stealth delay between sections
                stealth_delay("section")

            print(f"{Colors.CYAN}    ╚══{Colors.ENDC}")

    # Summary
    print(f"\n{Colors.BOLD}{Colors.YELLOW}    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Colors.ENDC}")
    print(f"{Colors.BOLD}    COMPLETION SUMMARY{Colors.ENDC}")
    print(f"{Colors.YELLOW}    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Colors.ENDC}")
    print(f"    {Colors.GREEN}✓ Completed: {completed_activities}{Colors.ENDC}")
    print(f"    {Colors.RED}✗ Failed: {failed_activities}{Colors.ENDC}")
    print(f"    {Colors.CYAN}● Total: {total_activities}{Colors.ENDC}")
    print(f"{Colors.YELLOW}    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Colors.ENDC}\n")

    input(f"    {Colors.DIM}Press Enter to continue...{Colors.ENDC}")

def select_chapters_menu(chapters_data):
    """Let user select which chapters to complete"""
    all_chapters = []
    for term in chapters_data:
        for chapter in term['chapters']:
            all_chapters.append({
                'number': chapter['number'],
                'title': chapter.get('title', f'Chapter {chapter["number"]}'),
                'sections': chapter['sections']
            })

    while True:
        clear_screen()
        print_banner()

        items = [f"Chapter {ch['number']}: {ch['title'][:40]}" for ch in all_chapters]
        items.append("── All Chapters ──")
        print_box("SELECT CHAPTERS", items)

        print_menu({
            '1-' + str(len(all_chapters)): 'Select a specific chapter',
            'A': 'Complete ALL chapters',
            'M': 'Select MULTIPLE chapters',
            'B': 'Go back'
        })

        choice = input(f"\n    {Colors.BOLD}Enter choice: {Colors.ENDC}").strip().upper()

        if choice == 'B':
            return None, None
        elif choice == 'A':
            return None, None  # None means all
        elif choice == 'M':
            chapters_input = input(f"    {Colors.BOLD}Enter chapter numbers (comma-separated, e.g., 1,3,5): {Colors.ENDC}").strip()
            try:
                selected = [int(x.strip()) for x in chapters_input.split(',')]
                return selected, None
            except:
                print(f"    {Colors.RED}Invalid input!{Colors.ENDC}")
                time.sleep(1)
        elif choice.isdigit():
            chapter_idx = int(choice) - 1
            if 0 <= chapter_idx < len(all_chapters):
                selected_chapter = all_chapters[chapter_idx]
                return select_sections_menu(selected_chapter)
        else:
            print(f"    {Colors.RED}Invalid choice!{Colors.ENDC}")
            time.sleep(1)

def select_sections_menu(chapter):
    """Let user select which sections to complete in a chapter"""
    while True:
        clear_screen()
        print_banner()

        print(f"\n{Colors.BOLD}{Colors.YELLOW}    Chapter {chapter['number']}: {chapter['title']}{Colors.ENDC}")

        items = [f"Section {chapter['number']}.{sec['number']}: {sec.get('title', 'Untitled')[:35]}"
                 for sec in chapter['sections']]
        items.append("── All Sections ──")
        print_box("SELECT SECTIONS", items)

        print_menu({
            '1-' + str(len(chapter['sections'])): 'Select a specific section',
            'A': 'Complete ALL sections in this chapter',
            'M': 'Select MULTIPLE sections',
            'B': 'Go back'
        })

        choice = input(f"\n    {Colors.BOLD}Enter choice: {Colors.ENDC}").strip().upper()

        if choice == 'B':
            return None, None
        elif choice == 'A':
            return [chapter['number']], None  # All sections in this chapter
        elif choice == 'M':
            sections_input = input(f"    {Colors.BOLD}Enter section numbers (comma-separated, e.g., 1,3,5): {Colors.ENDC}").strip()
            try:
                selected_nums = [int(x.strip()) for x in sections_input.split(',')]
                selected_sections = [(chapter['number'], num) for num in selected_nums]
                return [chapter['number']], selected_sections
            except:
                print(f"    {Colors.RED}Invalid input!{Colors.ENDC}")
                time.sleep(1)
        elif choice.isdigit():
            section_idx = int(choice) - 1
            if 0 <= section_idx < len(chapter['sections']):
                section = chapter['sections'][section_idx]
                return [chapter['number']], [(chapter['number'], section['number'])]
        else:
            print(f"    {Colors.RED}Invalid choice!{Colors.ENDC}")
            time.sleep(1)

def book_menu(token, user_id, buildkey, books):
    """Book selection menu"""
    global STEALTH_MODE
    while True:
        clear_screen()
        print_banner()

        # Show stealth mode status
        if STEALTH_MODE:
            print(f"{Colors.YELLOW}    ★ legit mode: ON - Realistic delays enabled{Colors.ENDC}")
        else:
            print(f"{Colors.DIM}    ○ legit mode: OFF - Fast mode{Colors.ENDC}")

        # Filter active books
        active_books = []
        for book in books:
           # if book.get('user_zybook_role') != 'Student':
             #   continue
           # if is_subscription_active(book):
               # active_books.append(book)
               active_books.append(book)

        if not active_books:
            print(f"\n    {Colors.RED}No active books found!{Colors.ENDC}")
            input(f"\n    {Colors.DIM}Press Enter to exit...{Colors.ENDC}")
            return

        items = [book.get('title', book['zybook_code'])[:50] for book in active_books]
        print_box("SELECT A BOOK", items)

        stealth_status = "ON ✓" if STEALTH_MODE else "OFF"
        print_menu({
            '1-' + str(len(active_books)): 'Select a book',
            'D': f'legit mode - Toggle legit mode [{stealth_status}]',
            'Q': 'Quit'
        })

        choice = input(f"\n    {Colors.BOLD}Enter choice: {Colors.ENDC}").strip().upper()

        if choice == 'Q':
            clear_screen()
            print(f"\n{Colors.CYAN}    goodbye {Colors.ENDC}\n")
            return
        elif choice == 'D':
            STEALTH_MODE = not STEALTH_MODE
            if STEALTH_MODE:
                print(f"\n{Colors.GREEN}    ★ legit mode activated! Realistic delays enabled.{Colors.ENDC}")
                print(f"{Colors.DIM}    Activities: 5-15s | Parts: 2-5s | Sections: 15-45s{Colors.ENDC}")
            else:
                print(f"\n{Colors.YELLOW}    ○ legit mode deactivated. Fast mode enabled.{Colors.ENDC}")
            time.sleep(1.5)
        elif choice.isdigit():
            book_idx = int(choice) - 1
            if 0 <= book_idx < len(active_books):
                selected_book = active_books[book_idx]
                zybook_code = selected_book['zybook_code']

                print(f"\n    {Colors.CYAN}Loading chapters...{Colors.ENDC}")
                chapters = get_chapters(token, zybook_code)

                if chapters:
                    selected_chapters, selected_sections = select_chapters_menu(chapters)
                    if selected_chapters is not None or selected_sections is not None or \
                       (selected_chapters is None and selected_sections is None):
                        # User made a selection (including "all")
                        run_completion(token, zybook_code, buildkey, chapters,
                                      selected_chapters, selected_sections)
                else:
                    print(f"    {Colors.RED}Could not load chapters!{Colors.ENDC}")
                    time.sleep(2)
        else:
            print(f"    {Colors.RED}Invalid choice!{Colors.ENDC}")
            time.sleep(1)

def main():
    # Enable ANSI colors on Windows
    if os.name == 'nt':
        os.system('')

    clear_screen()
    print_banner()

    print(f"{Colors.CYAN}    ─────────────────────────────────────{Colors.ENDC}")
    print(f"{Colors.BOLD}    ZYBOOKS LOGIN{Colors.ENDC}")
    print(f"{Colors.CYAN}    ─────────────────────────────────────{Colors.ENDC}")

    email = input(f"    {Colors.BOLD}Email: {Colors.ENDC}")
    password = getpass.getpass(f"    {Colors.BOLD}Password: {Colors.ENDC}")

    print(f"\n    {Colors.CYAN}Logging in...{Colors.ENDC}")
    result = login(email, password)

    if not result:
        print(f"    {Colors.RED}Login failed! Check your credentials.{Colors.ENDC}")
        input(f"\n    {Colors.DIM}Press Enter to exit...{Colors.ENDC}")
        return

    print_status(f"Logged in as {result['user'].get('first_name', 'User')}", "success")

    print(f"    {Colors.CYAN}Loading buildkey...{Colors.ENDC}")
    try:
        buildkey = get_buildkey()
        print_status("Buildkey loaded", "success")
    except Exception as e:
        print_status(f"Failed to get buildkey: {e}", "error")
        input(f"\n    {Colors.DIM}Press Enter to exit...{Colors.ENDC}")
        return

    token = result['session']['auth_token']
    user_id = result['user']['user_id']

    print(f"    {Colors.CYAN}Loading books...{Colors.ENDC}")
    books = get_books(token, user_id)
    print_status(f"Found {len(books)} book(s)", "success")

    time.sleep(1)

    # Enter main menu
    book_menu(token, user_id, buildkey, books)

if __name__ == '__main__':
    main()
