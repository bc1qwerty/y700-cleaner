"""
Lenovo Legion Y700 블로트웨어 제거 / 최적화 도구 (CLI)
========================================================
대상 기기: Lenovo Legion Y700 4세대 (TB322FC, ZUI ZUXOS, Android 16)
테스트 환경: Windows 11, ADB platform-tools 번들

주의: 이 도구는 CN_OPEN ROM (중국 내수판) 기준으로 패키지 목록을 구성했습니다.
      GL/Global ROM 은 일부 패키지명이 다를 수 있습니다.

사용법:
  py y700_cleaner.py                  # 대화형 모드
  py y700_cleaner.py --list           # 대상 목록만 출력
  py y700_cleaner.py --clean          # 앱 비활성화 실행
  py y700_cleaner.py --restore        # 복구
  py y700_cleaner.py --perf           # 기본 성능 설정 적용
  py y700_cleaner.py --perf-reset     # 기본 성능 설정 초기화
  py y700_cleaner.py --perf-optional  # 선택 설정 개별 확인 후 적용
"""

import subprocess
import sys
import shutil
import os

# Windows 콘솔 UTF-8
if sys.platform == "win32":
    os.system("chcp 65001 >nul 2>&1")
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# ── ADB 경로 ─────────────────────────────────────────────
if getattr(sys, "frozen", False):
    _BASE_DIR = os.path.dirname(sys.executable)
else:
    _BASE_DIR = os.path.dirname(os.path.abspath(__file__))

ADB_PATHS = [
    os.path.join(_BASE_DIR, "platform-tools", "adb.exe"),
    os.path.join(_BASE_DIR, "adb.exe"),
    "adb",
    os.path.expanduser(r"~\platform-tools\adb.exe"),
]


# ── 제거 대상 패키지 (pm uninstall -k --user 0) ──────────
# 모두 사용자 레벨 제거 — 공장초기화 시 자동 복구됨.
PACKAGES = {
    "Baidu / 중국 트래커": [
        ("com.baidu.map.location", "Baidu 위치추적"),
    ],
    "Lenovo CN 서비스": [
        ("com.lenovo.leos.appstore", "Lenovo 앱스토어 (CN)"),
        ("com.lenovo.leos.cloud.sync", "Lenovo 클라우드 동기화"),
        ("com.lenovo.lsf", "Lenovo 서비스 프레임워크"),
        ("com.lenovo.lsf.device", "Lenovo 서비스 프레임워크(기기)"),
        ("com.lenovo.xbb", "Lenovo 계정 (CN)"),
        ("com.lenovo.weathercenter", "Lenovo 날씨"),
        ("com.lenovo.lfh.tianjiao.tablet", "Tianjiao 교육 (CN)"),
        ("com.lenovo.lenovoprivacy", "Lenovo 개인정보 고지 (CN)"),
        ("com.lenovo.menu_assistant.hd", "플로팅 메뉴 어시스턴트"),
        ("com.lenovo.screensaver", "Lenovo 스크린세이버"),
    ],
    "Lenovo 텔레메트리": [
        ("com.lenovo.ue.device", "Lenovo UX 텔레메트리"),
        ("com.tblenovo.ue.config", "Lenovo UX 설정"),
    ],
    "Lenovo 푸시/광고": [
        ("com.tblenovo.lenovowhatsnew", "새로운 기능 알림"),
        ("com.tblenovo.tabpushout", "푸시 광고"),
        ("com.lenovo.xiaotian.trigger", "Xiaotian 트리거"),
    ],
    "Lenovo 음성/원격지원": [
        ("com.lenovo.levoice.caption", "Lenovo 음성 캡션"),
        ("com.lenovo.levoice_agent", "Lenovo 음성 에이전트"),
        ("com.tbsmart.levision", "Lenovo 원격지원 (LeVision)"),
        ("com.lmsa.app.lmsapad", "LMSA 패드 어시스턴트"),
    ],
    "공장/엔지니어링 테스트": [
        ("com.lenovo.EngineeringCode", "엔지니어링 코드"),
        ("com.yha.factory", "공장 테스트"),
        ("android.autoinstalls.config.Lenovo.tablet", "Lenovo 자동설치 설정"),
    ],
    "ZUI 선택 앱": [
        ("com.zui.browser", "ZUI 브라우저 (CN)"),
        ("com.zui.ai.lens", "AI 렌즈"),
        ("com.zui.ai.stylus", "AI 스타일러스"),
        ("com.zui.ai.aiservice", "AI 서비스"),
        ("com.zui.tassistent", "Tablet 어시스턴트"),
        ("com.zui.pp", "ZUI PP"),
        ("com.zui.pengen", "ZUI PenGen"),
        ("com.zui.SecretCode", "Secret Code"),
        ("com.zui.wallpapercropper", "배경화면 크롭"),
        ("com.zui.wallpapersetting", "배경화면 설정"),
        ("com.zui.net.data.monitor", "데이터 모니터"),
        ("com.zui.xlog", "ZUI xlog"),
        ("com.zui.contacts", "ZUI 연락처"),
        ("com.zui.camera.qr", "ZUI QR 스캐너"),
    ],
    "Android 불필요 앱": [
        ("com.android.printservice.recommendation", "인쇄 추천"),
        ("com.google.android.printservice.recommendation", "Google 인쇄 추천"),
        ("com.android.htmlviewer", "HTML 뷰어"),
        ("com.android.mms.service", "MMS 서비스"),
        ("com.android.wallpaperbackup", "배경화면 백업"),
        ("com.android.dreams.basic", "스크린세이버"),
        ("com.android.DeviceAsWebcam", "웹캠 모드"),
        ("com.android.managedprovisioning", "기기 프로비저닝"),
        ("com.android.emergency", "긴급 정보"),
        ("com.android.storagemanager", "저장공간 관리"),
        ("com.android.cellbroadcastreceiver", "긴급재난문자"),
        ("com.android.cellbroadcastservice", "긴급재난문자 서비스"),
    ],
    "Qualcomm XR/부가 서비스": [
        ("com.qualcomm.qti.xrwifi", "XR WiFi"),
        ("com.qualcomm.qti.xrvd.service", "XR 비디오"),
        ("com.qualcomm.qti.xrcb", "XR 콜백"),
        ("com.quicinc.voice.activation", "Qualcomm 음성 핫워드"),
    ],
    "SIM/통신 (Y700 WiFi-only)": [
        ("com.qualcomm.qti.lpa", "eSIM 프로비저닝"),
        ("com.qualcomm.qti.confdialer", "회의전화"),
        ("com.qualcomm.qti.simcontacts", "SIM 연락처"),
        ("com.qualcomm.qti.callfeaturessetting", "통화 기능 설정"),
        ("com.qualcomm.qti.uimGbaApp", "SIM 인증"),
        ("com.qualcomm.uimremoteserver", "SIM 원격 서버"),
        ("com.qualcomm.uimremoteclient", "SIM 원격 클라이언트"),
        ("com.qualcomm.qti.remoteSimlockAuth", "SIM 잠금 인증"),
        ("com.qualcomm.qti.poweroffalarm", "전원꺼짐 알람"),
        ("com.qti.xdivert", "착신전환"),
        ("com.qti.dcf", "DCF"),
        ("com.qti.ltebc", "LTE Broadcast Cell"),
        ("com.android.imsserviceentitlement", "IMS 서비스 권한"),
        ("com.android.simappdialog", "SIM 앱 다이얼로그"),
    ],
    "Ready For (PC 모드 미사용 시)": [
        # 'leapp://ptn/...' 딥링크가 com.lenovo.leos.appstore 를 호출하는데
        # 본 도구가 leos.appstore 를 제거하므로 ActivityNotFoundException 으로
        # com.motorola.mobiledesktop 이 백그라운드에서 충돌함.
        # PC 모니터/Ready For 미사용 시 함께 제거하는 게 깨끗함.
        ("com.motorola.mobiledesktop", "Ready For (Mobile Desktop)"),
        ("com.motorola.mobiledesktop.core", "Ready For Core"),
        ("com.motorola.readyforsignature.app", "Ready For Signature"),
    ],
}


# ── 절대 건드리지 않을 패키지 (코어/런처/키보드/연결) ──────
# Boox 의 com.onyx.kreader 사건 (ContentProvider 하드 의존성 → 부팅 크래시) 교훈 반영.
# Y700 은 아직 static analysis 가 되지 않았으므로 ZUI 코어 전체를 보수적으로 보호.
KEEP_PACKAGES = {
    # ZUI 코어/런처/UI
    "com.zui.launcher": "ZUI 런처 (홈)",
    "com.zui.desktoplauncher": "데스크톱 모드 런처",
    "com.zui.setupwizard": "초기 설정 마법사",
    "com.zui.cores": "ZUI 코어 서비스",
    "com.zui.engine": "ZUI 엔진",
    "com.zui.resolver": "Activity Resolver",
    "com.zui.safecenter": "설정 (Safe Center)",
    "com.zui.homesettings": "홈 설정",
    "com.zui.keyboardupdate.olympia": "ZUI 키보드",
    "com.zui.deviceidservice": "기기 ID 서비스",
    "com.zui.themes.provider": "테마 Provider",
    "com.zui.dynamic.color.overlay": "Material You 색상",
    "com.zui.freeform.sidebar": "플로팅 사이드바",
    "com.zui.filemanager": "파일 관리자",
    "com.zui.camera": "카메라",
    "com.zui.gallery": "갤러리",
    # Lenovo 기능
    "com.lenovo.hyperengine": "HyperEngine 게임 가속",
    "com.lenovo.tab_extreme": "Tab Extreme (게이밍 모드)",
    "com.lenovo.penservice": "스타일러스 서비스",
    "com.lenovo.screensplit": "화면 분할",
    "com.lenovo.tbengine": "Tab 엔진",
    "com.dolby.daxservice": "Dolby Atmos",
    "com.dolby.dolbyvisionservice": "Dolby Vision",
    # 시스템 settings provider (motorola.mobiledesktop 와 별개)
    "com.motorola.android.providers.settings": "Motorola Settings Provider (시스템)",
    # ── 더 많은 연결 ANR 회피용 (2026-05-03 검증) ──
    # Lenovo 커스텀 'MoreConnectionsSettings' Fragment 가 binder 호출하는 컴포넌트.
    # 빠뜨리고 제거하면 설정 → 더 많은 연결 5초 ANR 발생.
    "com.qualcomm.qti.cne": "Connectivity Network Engine (연결 의존)",
    "com.android.printspooler": "인쇄 스풀러 (더 많은 연결 Print)",
    "com.android.bips": "BIPS 인쇄 (더 많은 연결 Print)",
    "vendor.qti.bluetooth.xpan": "BT XPAN (더 많은 연결 BT 확장)",
    "vendor.qti.data.ntnsatapp": "위성 통신 (Android 14+ 표준 항목)",
    "com.qualcomm.qti.uceShimService": "UCE Shim (통신 컴포넌트)",
    "vendor.qti.imsrcs": "IMS RCS (통신 컴포넌트)",
    "vendor.qti.imsdatachannel": "IMS 데이터채널 (통신 컴포넌트)",
    "com.android.smspush": "SMS Push (더 많은 연결 의존)",
    "com.android.bluetoothmidiservice": "BT MIDI (더 많은 연결 의존)",
    "com.android.hotspot2.osulogin": "핫스팟 2.0 로그인 (더 많은 연결 의존)",
    "com.wapi.wapicertmanage": "WAPI 인증서 (더 많은 연결 WiFi 보안)",
}


# ── 성능 최적화 설정 (기본) ───────────────────────────────
# "전체 선택" 대상. 일반적으로 안전하고 대부분의 사용자에게 유익.
PERFORMANCE_SETTINGS = [
    {
        "key": "window_animation_scale",
        "name": "창 애니메이션 0.5배",
        "desc": "UI 반응속도 향상",
        "namespace": "global",
        "on_value": "0.5",
        "off_value": "1.0",
    },
    {
        "key": "transition_animation_scale",
        "name": "전환 애니메이션 0.5배",
        "desc": "화면 전환 가속",
        "namespace": "global",
        "on_value": "0.5",
        "off_value": "1.0",
    },
    {
        "key": "animator_duration_scale",
        "name": "애니메이터 0.5배",
        "desc": "전체 애니메이션 가속",
        "namespace": "global",
        "on_value": "0.5",
        "off_value": "1.0",
    },
    {
        "key": "ble_scan_always_enabled",
        "name": "BLE 항상 스캔 끄기",
        "desc": "백그라운드 블루투스 스캔 중단",
        "namespace": "global",
        "on_value": "0",
        "off_value": "1",
    },
    {
        "key": "wifi_scan_always_enabled",
        "name": "WiFi 항상 스캔 끄기",
        "desc": "백그라운드 WiFi 스캔 중단",
        "namespace": "global",
        "on_value": "0",
        "off_value": "1",
    },
    {
        "key": "heads_up_notifications_enabled",
        "name": "알림 팝업 비활성화",
        "desc": "헤드업 알림 끄기",
        "namespace": "global",
        "on_value": "0",
        "off_value": "1",
    },
    {
        "key": "package_verifier_enable",
        "name": "Play Protect 앱 검증 끄기",
        "desc": "사이드로드 설치 가속 (F-Droid/Obtainium 대응)",
        "namespace": "global",
        "on_value": "0",
        "off_value": "1",
    },
    {
        "key": "verifier_verify_adb_installs",
        "name": "ADB 설치 검증 끄기",
        "desc": "adb install 시마다 뜨는 승인 팝업 제거",
        "namespace": "global",
        "on_value": "0",
        "off_value": "1",
    },
    {
        "key": "stay_on_while_plugged_in",
        "name": "충전 중 화면 켜둠",
        "desc": "AC/USB/무선 충전 시 화면 자동 꺼짐 방지",
        "namespace": "global",
        "on_value": "7",
        "off_value": "0",
    },
]

# ── 선택 설정 (opt-in 전용) ────────────────────────────────
# 전체 선택 대상 아님. 개별 체크로만 적용. 성향/환경에 따라 다름.
# extras: [(key, on_value, off_value)] — on_value 적용 시 함께 설정,
#         off_value 가 None 이면 reset 시 settings delete.
OPTIONAL_SETTINGS = [
    {
        "key": "private_dns_mode",
        "name": "Private DNS (AdGuard)",
        "desc": "광고/트래커 차단 DNS (dns.adguard.com) 강제 사용",
        "namespace": "global",
        "on_value": "hostname",
        "off_value": "opportunistic",
        "extras": [
            ("private_dns_specifier", "dns.adguard.com", None),
        ],
    },
    {
        "key": "haptic_feedback_enabled",
        "name": "햅틱 피드백 끄기",
        "desc": "터치/키보드 진동 완전 비활성화",
        "namespace": "system",
        "on_value": "0",
        "off_value": "1",
    },
    {
        "key": "adb_wifi_enabled",
        "name": "ADB over WiFi 활성화",
        "desc": "USB 없이 무선 디버깅 (최초 1회 기기에서 페어링 필요)",
        "namespace": "global",
        "on_value": "1",
        "off_value": "0",
    },
]


def find_adb() -> str:
    for path in ADB_PATHS:
        if os.path.isfile(path):
            return path
        if shutil.which(path):
            return path
    return ""


def run_adb(*args) -> tuple[int, str]:
    adb = find_adb()
    if not adb:
        print("[ERROR] ADB를 찾을 수 없습니다. platform-tools 경로를 확인하세요.")
        sys.exit(1)
    try:
        r = subprocess.run(
            [adb, *args],
            capture_output=True, text=True, timeout=30,
            encoding="utf-8", errors="replace",
        )
        return r.returncode, r.stdout.strip()
    except subprocess.TimeoutExpired:
        return 1, "timeout"


def check_device() -> bool:
    _, out = run_adb("devices")
    lines = [l for l in out.splitlines() if "\tdevice" in l]
    if not lines:
        print("[ERROR] 연결된 기기가 없습니다.")
        print("  - USB 케이블 연결 확인")
        print("  - 개발자 옵션 > USB 디버깅 활성화")
        print("  - 'USB 디버깅 허용' 팝업에서 허용")
        return False
    device_id = lines[0].split("\t")[0]
    _, model = run_adb("shell", "getprop", "ro.product.model")
    print(f"[OK] 기기 연결됨: {device_id} ({model.strip()})")
    if model.strip() != "TB322FC":
        print(f"[WARN] 이 도구는 TB322FC(Y700 4세대) 기준입니다. 현재 모델: {model.strip()}")
        print("       일부 패키지명이 다를 수 있으니 신중하게 진행하세요.")
    return True


def get_installed_packages() -> set[str]:
    _, out = run_adb("shell", "pm", "list", "packages", "-e")
    return {line.replace("package:", "").strip() for line in out.splitlines() if line.startswith("package:")}


def list_packages():
    installed = get_installed_packages()
    total = 0
    for category, pkgs in PACKAGES.items():
        targets = [(p, n) for p, n in pkgs if p in installed]
        if not targets:
            continue
        print(f"\n── {category} ({len(targets)}개) ──")
        for pkg, name in targets:
            print(f"  {name:<25s}  {pkg}")
            total += 1
    if total == 0:
        print("\n이미 모두 제거/비활성화되었습니다!")
    else:
        print(f"\n총 {total}개 제거 가능")
    print(f"\n── 유지 권장 (건드리지 말 것) ──")
    for pkg, desc in KEEP_PACKAGES.items():
        status = "설치됨" if pkg in installed else "없음"
        print(f"  [{status}] {desc:<25s}  ({pkg})")


def clean_packages():
    installed = get_installed_packages()
    all_pkgs = [(p, n, c) for c, pkgs in PACKAGES.items() for p, n in pkgs]
    targets = [(p, n, c) for p, n, c in all_pkgs if p in installed]

    if not targets:
        print("제거할 앱이 없습니다.")
        return

    print(f"\n{len(targets)}개 앱을 제거합니다...\n")
    success, fail = 0, 0
    for pkg, name, _ in targets:
        _, out = run_adb("shell", "pm", "uninstall", "-k", "--user", "0", pkg)
        if "Success" in out:
            print(f"  [OK] {name} ({pkg})")
            success += 1
        else:
            print(f"  [FAIL] {name} ({pkg}) - {out}")
            fail += 1
    print(f"\n완료: {success}개 제거, {fail}개 실패")
    if success > 0:
        print("복구: py y700_cleaner.py --restore")


def restore_packages():
    installed = get_installed_packages()
    all_pkgs = [(p, n) for pkgs in PACKAGES.values() for p, n in pkgs]
    removed = [(p, n) for p, n in all_pkgs if p not in installed]

    if not removed:
        print("복구할 앱이 없습니다.")
        return

    print(f"\n{len(removed)}개 앱을 복구합니다...\n")
    success, fail = 0, 0
    for pkg, name in removed:
        code, out = run_adb("shell", "cmd", "package", "install-existing", pkg)
        if code == 0 and "install" in out.lower():
            print(f"  [OK] {name} ({pkg})")
            success += 1
        else:
            print(f"  [FAIL] {name} ({pkg}) - {out}")
            fail += 1
    print(f"\n완료: {success}개 복구, {fail}개 실패")


def _apply_setting(s: dict, action: str):
    """단일 설정과 그 extras 를 적용/초기화."""
    value = s["on_value"] if action == "apply" else s["off_value"]
    run_adb("shell", "settings", "put", s["namespace"], s["key"], value)
    for extra in s.get("extras", []):
        ekey, eon, eoff = extra
        if action == "apply":
            run_adb("shell", "settings", "put", s["namespace"], ekey, eon)
        elif eoff is None:
            run_adb("shell", "settings", "delete", s["namespace"], ekey)
        else:
            run_adb("shell", "settings", "put", s["namespace"], ekey, eoff)


def apply_perf():
    print(f"\n{len(PERFORMANCE_SETTINGS)}개 기본 성능 설정을 적용합니다...\n")
    for s in PERFORMANCE_SETTINGS:
        _apply_setting(s, "apply")
        print(f"  [OK] {s['name']} → {s['on_value']}")
    print("\n기본 성능 설정 적용 완료 (선택 설정은 --perf-optional 로 개별 적용)")


def reset_perf():
    print(f"\n{len(PERFORMANCE_SETTINGS)}개 기본 성능 설정을 초기화합니다...\n")
    for s in PERFORMANCE_SETTINGS:
        _apply_setting(s, "reset")
        print(f"  [OK] {s['name']} → {s['off_value']}")
    print("\n기본 성능 설정 초기화 완료")


def apply_optional():
    """선택 설정을 대화형으로 하나씩 묻고 적용."""
    print(f"\n{len(OPTIONAL_SETTINGS)}개의 선택 설정이 있습니다 (개별 확인).\n")
    print("각 항목은 기본적으로 적용되지 않으며, 직접 y 를 입력해야만 적용됩니다.\n")
    applied = 0
    for s in OPTIONAL_SETTINGS:
        print(f"  [{s['name']}]")
        print(f"     {s['desc']}")
        ans = input(f"     적용할까요? (y/N): ").strip().lower()
        if ans == "y":
            _apply_setting(s, "apply")
            print(f"     [OK] 적용됨 → {s['on_value']}\n")
            applied += 1
        else:
            print(f"     건너뜀\n")
    print(f"선택 설정 처리 완료: {applied}/{len(OPTIONAL_SETTINGS)} 적용됨")


def interactive_mode():
    print("=" * 56)
    print("  Lenovo Legion Y700 Cleaner")
    print("=" * 56)
    print()
    print("대상 기기: Y700 4세대 (TB322FC, ZUI ZUXOS, Android 16)")
    print("테스트 환경: Windows 11 + ADB platform-tools")
    print()
    print("모든 작업은 `pm uninstall -k --user 0` (사용자 레벨)")
    print("또는 `settings put` (전역 설정) 으로 이뤄지며,")
    print("공장초기화 시 전부 자동 복구됩니다.")
    print()

    if not check_device():
        return

    print()
    print("[1] 제거 대상 목록 보기")
    print("[2] 블로트웨어 제거 실행")
    print("[3] 제거한 앱 복구")
    print("[4] 기본 성능 설정 적용 (애니메이션 0.5배 등)")
    print("[5] 기본 성능 설정 초기화")
    print("[6] 선택 설정 개별 적용 (Private DNS, 햅틱 끄기, ADB over WiFi)")
    print("[q] 종료")
    print()

    choice = input("선택: ").strip()
    if choice == "1":
        list_packages()
    elif choice == "2":
        list_packages()
        print()
        confirm = input("위 앱들을 제거하시겠습니까? (y/N): ").strip().lower()
        if confirm == "y":
            clean_packages()
        else:
            print("취소됨.")
    elif choice == "3":
        restore_packages()
    elif choice == "4":
        apply_perf()
    elif choice == "5":
        reset_perf()
    elif choice == "6":
        apply_optional()
    elif choice == "q":
        print("종료.")
    else:
        print("잘못된 선택입니다.")


def main():
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        if arg == "--list":
            if check_device():
                list_packages()
        elif arg == "--clean":
            if check_device():
                clean_packages()
        elif arg == "--restore":
            if check_device():
                restore_packages()
        elif arg == "--perf":
            if check_device():
                apply_perf()
        elif arg == "--perf-reset":
            if check_device():
                reset_perf()
        elif arg == "--perf-optional":
            if check_device():
                apply_optional()
        elif arg in ("--help", "-h"):
            print(__doc__)
        else:
            print(f"알 수 없는 옵션: {arg}")
            print("사용법: py y700_cleaner.py [--list|--clean|--restore|--perf|--perf-reset|--perf-optional]")
    else:
        interactive_mode()


if __name__ == "__main__":
    main()
