"""
Y700 Cleaner - GUI v1.0
========================
Lenovo Legion Y700 3세대 (TB322FC) 블로트웨어 제거 + 최적화 GUI.
기기를 자동 감지하여 맞춤 목록을 표시합니다.

지원 기기:
  - Lenovo Legion Y700 3세대 (TB322FC, ZUI ZUXOS, Android 16 / SDK 36)

설계 원칙 (boox-cleaner 교훈 반영):
  - 모든 작업은 사용자 레벨 (공장초기화 시 복구)
  - ZUI 런처/코어/키보드/게이밍 엔진 등은 KEEP_PACKAGES 로 보호
  - 분석되지 않은 패키지는 기본 목록에 포함하지 않음
"""

VERSION = "1.1"

import subprocess
import sys
import os
import shutil
import threading
from datetime import datetime

import customtkinter as ctk

# ── ADB ──────────────────────────────────────────────────
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

# ── 기기 프로필 ──────────────────────────────────────────

DEVICE_PROFILES = {
    "TB322FC": {
        "display_name": "Lenovo Legion Y700 (3세대)",
        "codename": "TB322FC",
        "firmware": "ZUI ZUXOS 1.5.x",
        "android": "16 (API 36)",
        "platform": "Qualcomm sun",
        "region": "CN_OPEN (중국 내수판)",
    },
}

# ── 앱 제거 대상 (pm uninstall -k --user 0) ─────────────
# 모두 사용자 레벨 — 공장초기화 시 자동 복구됨.

PACKAGES = {
    "Baidu / 중국 트래커": [
        ("com.baidu.map.location", "Baidu 위치추적"),
    ],
    "Lenovo CN 서비스": [
        ("com.lenovo.leos.appstore", "Lenovo 앱스토어 (CN)"),
        ("com.lenovo.leos.cloud.sync", "Lenovo 클라우드 동기화"),
        ("com.lenovo.lsf", "Lenovo 서비스 프레임워크"),
        ("com.lenovo.lsf.device", "Lenovo 서비스 프레임워크 (기기)"),
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
    "WAPI (중국 WiFi 인증)": [
        ("com.wapi.wapicertmanage", "WAPI 인증서 관리자"),
    ],
    "Android 불필요 앱": [
        ("com.android.printspooler", "인쇄 스풀러"),
        ("com.android.bips", "BIPS 인쇄"),
        ("com.android.printservice.recommendation", "인쇄 추천"),
        ("com.google.android.printservice.recommendation", "Google 인쇄 추천"),
        ("com.android.htmlviewer", "HTML 뷰어"),
        ("com.android.smspush", "SMS Push"),
        ("com.android.mms.service", "MMS 서비스"),
        ("com.android.wallpaperbackup", "배경화면 백업"),
        ("com.android.dreams.basic", "스크린세이버"),
        ("com.android.DeviceAsWebcam", "웹캠 모드"),
        ("com.android.hotspot2.osulogin", "핫스팟 2.0 로그인"),
        ("com.android.managedprovisioning", "기기 프로비저닝"),
        ("com.android.emergency", "긴급 정보"),
        ("com.android.storagemanager", "저장공간 관리"),
        ("com.android.cellbroadcastreceiver", "긴급재난문자"),
        ("com.android.cellbroadcastservice", "긴급재난문자 서비스"),
        ("com.android.bluetoothmidiservice", "블루투스 MIDI 서비스"),
    ],
    "Qualcomm XR/부가 서비스": [
        ("com.qualcomm.qti.xrwifi", "XR WiFi"),
        ("com.qualcomm.qti.xrvd.service", "XR 비디오"),
        ("com.qualcomm.qti.xrcb", "XR 콜백"),
        ("com.quicinc.voice.activation", "Qualcomm 음성 핫워드"),
        ("vendor.qti.bluetooth.xpan", "BT XPAN"),
        ("vendor.qti.data.ntnsatapp", "위성 통신"),
        ("com.qualcomm.qti.cne", "Connectivity Network Engine"),
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
        ("com.qualcomm.qti.uceShimService", "UCE Shim"),
        ("com.qualcomm.qti.poweroffalarm", "전원꺼짐 알람"),
        ("com.qti.xdivert", "착신전환"),
        ("com.qti.dcf", "DCF"),
        ("com.qti.ltebc", "LTE Broadcast Cell"),
        ("com.android.imsserviceentitlement", "IMS 서비스 권한"),
        ("com.android.simappdialog", "SIM 앱 다이얼로그"),
        ("vendor.qti.imsrcs", "IMS RCS"),
        ("vendor.qti.imsdatachannel", "IMS 데이터채널"),
    ],
}

# ── 절대 건드리지 않을 패키지 (코어/런처/키보드/게이밍) ─────
# Boox 의 com.onyx.kreader 사건 (ContentProvider 하드 의존성 → 부팅 크래시) 교훈 반영.
# Y700 은 아직 static analysis 가 되지 않았으므로 ZUI 코어 전체를 보수적으로 보호.
KEEP_PACKAGES = {
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
    "com.lenovo.hyperengine": "HyperEngine 게임 가속",
    "com.lenovo.tab_extreme": "Tab Extreme (게이밍 모드)",
    "com.lenovo.penservice": "스타일러스 서비스",
    "com.lenovo.screensplit": "화면 분할",
    "com.lenovo.tbengine": "Tab 엔진",
    "com.motorola.mobiledesktop.core": "Ready For (PC 모드)",
    "com.dolby.daxservice": "Dolby Atmos",
    "com.dolby.dolbyvisionservice": "Dolby Vision",
}

# ── 성능 최적화 설정 ─────────────────────────────────────

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
]


# ── ADB 유틸 ─────────────────────────────────────────────

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
        return 1, "ADB를 찾을 수 없습니다"
    try:
        r = subprocess.run(
            [adb, *args],
            capture_output=True, text=True, timeout=30,
            encoding="utf-8", errors="replace",
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
        )
        return r.returncode, r.stdout.strip()
    except subprocess.TimeoutExpired:
        return 1, "타임아웃"
    except Exception as e:
        return 1, str(e)


def get_device() -> str | None:
    _, out = run_adb("devices")
    for line in out.splitlines():
        if "\tdevice" in line:
            return line.split("\t")[0]
    return None


def get_device_model() -> str:
    _, out = run_adb("shell", "getprop", "ro.product.device")
    return out.strip()


def get_device_info() -> dict[str, str]:
    props = {
        "model": "ro.product.model",
        "device": "ro.product.device",
        "brand": "ro.product.brand",
        "firmware": "ro.build.display.id",
        "android": "ro.build.version.release",
        "sdk": "ro.build.version.sdk",
        "platform": "ro.board.platform",
        "security_patch": "ro.build.version.security_patch",
    }
    info = {}
    for key, prop in props.items():
        _, val = run_adb("shell", "getprop", prop)
        info[key] = val.strip()
    return info


def get_installed_packages() -> set[str]:
    _, out = run_adb("shell", "pm", "list", "packages", "-e")
    return {line.replace("package:", "").strip() for line in out.splitlines() if line.startswith("package:")}


def get_disabled_packages() -> set[str]:
    _, out = run_adb("shell", "pm", "list", "packages", "-d")
    return {line.replace("package:", "").strip() for line in out.splitlines() if line.startswith("package:")}


# ── GUI ──────────────────────────────────────────────────

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title(f"Y700 Cleaner v{VERSION}")
        self.geometry("820x880")
        self.minsize(720, 720)
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.installed: set[str] = set()
        self.disabled: set[str] = set()
        self.app_checkboxes: dict[str, tuple[ctk.CTkCheckBox, ctk.BooleanVar]] = {}
        self._current_device: str | None = None
        self._current_model: str = ""

        self._build_ui()
        self._start_device_monitor()

    def _build_ui(self):
        # 상단: 기기 상태
        top = ctk.CTkFrame(self)
        top.pack(fill="x", padx=12, pady=(12, 6))

        self.status_label = ctk.CTkLabel(top, text="기기 연결 확인 중...", font=("", 14, "bold"))
        self.status_label.pack(side="left", padx=8, pady=8)

        self.refresh_btn = ctk.CTkButton(top, text="새로고침", width=90, command=self._refresh_device)
        self.refresh_btn.pack(side="right", padx=8, pady=8)

        # 기기 정보
        self.info_frame = ctk.CTkFrame(self)
        self.info_frame.pack(fill="x", padx=12, pady=(0, 4))

        self.info_label = ctk.CTkLabel(
            self.info_frame,
            text="기기를 연결하면 자동으로 모델을 감지합니다.\n\n"
                 "지원 기기: Lenovo Legion Y700 3세대 (TB322FC)\n"
                 "모든 제거/비활성화는 공장초기화 시 자동 복구됩니다.",
            font=("Consolas", 11), text_color="gray", justify="left", anchor="w",
        )
        self.info_label.pack(padx=10, pady=6, anchor="w")

        # 탭
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=12, pady=6)

        self.tab_apps = self.tabview.add("앱 제거")
        self.tab_perf = self.tabview.add("성능 최적화")

        self._build_apps_tab()
        self._build_perf_tab()

        # 로그
        self.log_box = ctk.CTkTextbox(self, height=140, font=("Consolas", 12))
        self.log_box.pack(fill="x", padx=12, pady=(0, 12))
        self.log_box.configure(state="disabled")

    # ── 앱 제거 탭 ───────────────────────────────────────

    def _build_apps_tab(self):
        self.app_list_frame = ctk.CTkScrollableFrame(self.tab_apps)
        self.app_list_frame.pack(fill="both", expand=True, pady=(0, 4))

        sel = ctk.CTkFrame(self.tab_apps)
        sel.pack(fill="x", pady=(0, 4))
        ctk.CTkButton(sel, text="전체 선택", width=90, command=lambda: self._select_all(True)).pack(side="left", padx=4, pady=4)
        ctk.CTkButton(sel, text="전체 해제", width=90, command=lambda: self._select_all(False)).pack(side="left", padx=4, pady=4)
        self.app_count_label = ctk.CTkLabel(sel, text="", font=("", 12))
        self.app_count_label.pack(side="right", padx=8, pady=4)

        btn = ctk.CTkFrame(self.tab_apps)
        btn.pack(fill="x")
        self.app_clean_btn = ctk.CTkButton(btn, text="선택 앱 제거", fg_color="#c0392b", hover_color="#e74c3c", command=self._on_app_clean)
        self.app_clean_btn.pack(side="left", padx=4, pady=4, expand=True, fill="x")
        self.app_restore_btn = ctk.CTkButton(btn, text="선택 앱 복구", fg_color="#2980b9", hover_color="#3498db", command=self._on_app_restore)
        self.app_restore_btn.pack(side="left", padx=4, pady=4, expand=True, fill="x")

    # ── 성능 최적화 탭 ───────────────────────────────────

    def _build_perf_tab(self):
        self.perf_frame = ctk.CTkScrollableFrame(self.tab_perf)
        self.perf_frame.pack(fill="both", expand=True, pady=(0, 4))

        self.perf_vars: dict[str, ctk.BooleanVar] = {}
        for s in PERFORMANCE_SETTINGS:
            var = ctk.BooleanVar(value=False)
            frame = ctk.CTkFrame(self.perf_frame)
            frame.pack(fill="x", padx=4, pady=2)
            cb = ctk.CTkCheckBox(frame, text=f"  {s['name']}", variable=var, font=("", 12))
            cb.pack(side="left", padx=8, pady=4)
            desc = ctk.CTkLabel(frame, text=s["desc"], font=("", 11), text_color="gray")
            desc.pack(side="left", padx=8, pady=4)
            self.perf_vars[s["key"]] = var

        btn = ctk.CTkFrame(self.tab_perf)
        btn.pack(fill="x")
        self.perf_apply_btn = ctk.CTkButton(btn, text="선택 항목 적용", fg_color="#27ae60", hover_color="#2ecc71", command=self._on_perf_apply)
        self.perf_apply_btn.pack(side="left", padx=4, pady=4, expand=True, fill="x")
        self.perf_reset_btn = ctk.CTkButton(btn, text="선택 항목 초기화", fg_color="#7f8c8d", hover_color="#95a5a6", command=self._on_perf_reset)
        self.perf_reset_btn.pack(side="left", padx=4, pady=4, expand=True, fill="x")

    # ── 로그 ─────────────────────────────────────────────

    def _log(self, msg: str):
        ts = datetime.now().strftime("%H:%M:%S")
        self.log_box.configure(state="normal")
        self.log_box.insert("end", f"[{ts}] {msg}\n")
        self.log_box.see("end")
        self.log_box.configure(state="disabled")

    # ── 기기 정보 ────────────────────────────────────────

    def _update_device_info(self, device_code: str):
        profile = DEVICE_PROFILES.get(device_code)
        if profile:
            info_text = (
                f"감지된 기기: {profile['display_name']}\n"
                f"  코드명: {profile['codename']} · 펌웨어: {profile['firmware']}\n"
                f"  Android: {profile['android']} · 플랫폼: {profile['platform']}\n"
                f"  리전: {profile['region']}"
            )
        else:
            info = get_device_info()
            info_text = (
                f"감지된 기기: {info.get('model', '알 수 없음')} (미등록 모델)\n"
                f"  코드명: {info.get('device', '-')} · 브랜드: {info.get('brand', '-')}\n"
                f"  펌웨어: {info.get('firmware', '-')}\n"
                f"  Android: {info.get('android', '-')} (API {info.get('sdk', '-')}) · 플랫폼: {info.get('platform', '-')}"
            )
        warn = "\n\n⚠ 모든 제거/비활성화는 공장초기화 시 자동 복구됨"
        self.info_label.configure(text=info_text + warn)

    # ── 기기 자동 감지 ───────────────────────────────────

    def _start_device_monitor(self):
        def poll():
            device = get_device()
            model = get_device_model() if device else ""
            self.after(0, self._on_device_poll, device, model)
        threading.Thread(target=poll, daemon=True).start()

    def _on_device_poll(self, device: str | None, model: str):
        prev = self._current_device
        self._current_device = device

        if device and not prev:
            self._on_device_connected(device, model)
        elif not device and prev:
            self.status_label.configure(text="기기 없음 — USB 디버깅 확인", text_color="#e74c3c")
            self._log("기기 연결 해제됨")
            self._current_model = ""
        elif device and prev and device != prev:
            self._on_device_connected(device, model)

        self.after(3000, self._start_device_monitor)

    def _on_device_connected(self, device: str, model: str):
        self._current_model = model
        display = DEVICE_PROFILES.get(model, {}).get("display_name", model)
        self.status_label.configure(text=f"연결됨: {display} ({device})", text_color="#2ecc71")
        self._log(f"기기 연결됨: {display} ({device})")
        self._update_device_info(model)
        self._refresh_all()

    def _refresh_device(self):
        device = get_device()
        self._current_device = device
        if device:
            model = get_device_model()
            self._on_device_connected(device, model)
        else:
            self.status_label.configure(text="기기 없음 — USB 디버깅 확인", text_color="#e74c3c")
            self._log("기기를 찾을 수 없습니다")

    def _refresh_all(self):
        self.installed = get_installed_packages()
        self.disabled = get_disabled_packages()
        self._refresh_app_list()
        self._refresh_perf_status()

    # ── 앱 목록 ──────────────────────────────────────────

    def _refresh_app_list(self):
        for w in self.app_list_frame.winfo_children():
            w.destroy()
        self.app_checkboxes.clear()
        total = 0

        for category, pkgs in PACKAGES.items():
            has_any = any(p in self.installed for p, _ in pkgs)
            exists = [p for p, _ in pkgs if p in self.installed or p in self.disabled]
            if not exists:
                continue
            cat_text = f"── {category}{'' if has_any else ' (모두 제거됨)'} ──"
            cat_color = "white" if has_any else "gray"
            ctk.CTkLabel(self.app_list_frame, text=cat_text, font=("", 12, "bold"), text_color=cat_color).pack(anchor="w", padx=4, pady=(10, 2))

            for pkg, name in pkgs:
                if pkg not in self.installed and pkg not in self.disabled:
                    continue
                var = ctk.BooleanVar(value=False)
                is_installed = pkg in self.installed
                if is_installed:
                    var.set(True)
                    total += 1
                status = "" if is_installed else " [제거됨]"
                color = "white" if is_installed else "gray"
                cb = ctk.CTkCheckBox(self.app_list_frame, text=f"  {name}{status}  ({pkg})", variable=var, font=("", 12), text_color=color)
                cb.pack(anchor="w", padx=16, pady=1)
                self.app_checkboxes[pkg] = (cb, var)

        ctk.CTkLabel(self.app_list_frame, text="── 유지 권장 (제거 금지) ──", font=("", 12, "bold"), text_color="#f39c12").pack(anchor="w", padx=4, pady=(10, 2))
        for pkg, desc in KEEP_PACKAGES.items():
            status = "설치됨" if pkg in self.installed else "없음"
            ctk.CTkLabel(self.app_list_frame, text=f"  [{status}] {desc}  ({pkg})", font=("", 12), text_color="#f39c12").pack(anchor="w", padx=16, pady=1)

        self.app_count_label.configure(text=f"{total}개 제거 가능")

    # ── 성능 상태 ────────────────────────────────────────

    def _refresh_perf_status(self):
        for s in PERFORMANCE_SETTINGS:
            _, val = run_adb("shell", "settings", "get", s["namespace"], s["key"])
            val = val.strip()
            is_optimized = (val == s["on_value"])
            self.perf_vars[s["key"]].set(is_optimized)

    # ── 공통 유틸 ────────────────────────────────────────

    def _select_all(self, state: bool):
        for _, (cb, var) in self.app_checkboxes.items():
            var.set(state)

    def _set_all_buttons(self, enabled: bool):
        state = "normal" if enabled else "disabled"
        for btn in [self.app_clean_btn, self.app_restore_btn, self.perf_apply_btn, self.perf_reset_btn, self.refresh_btn]:
            btn.configure(state=state)

    # ── 앱 제거/복구 ────────────────────────────────────

    def _on_app_clean(self):
        all_pkgs = {p: n for pkgs in PACKAGES.values() for p, n in pkgs}
        selected = [(pkg, all_pkgs.get(pkg, pkg)) for pkg, (_, var) in self.app_checkboxes.items() if var.get() and pkg in self.installed]
        if not selected:
            self._log("제거할 앱이 없습니다")
            return
        self._set_all_buttons(False)
        self._log(f"{len(selected)}개 앱 제거 시작...")
        threading.Thread(target=self._do_app_action, args=(selected, "uninstall"), daemon=True).start()

    def _on_app_restore(self):
        all_pkgs = {p: n for pkgs in PACKAGES.values() for p, n in pkgs}
        selected = [(pkg, all_pkgs.get(pkg, pkg)) for pkg, (_, var) in self.app_checkboxes.items() if var.get() and pkg not in self.installed]
        if not selected:
            self._log("복구할 앱이 없습니다")
            return
        self._set_all_buttons(False)
        self._log(f"{len(selected)}개 앱 복구 시작...")
        threading.Thread(target=self._do_app_action, args=(selected, "restore"), daemon=True).start()

    def _do_app_action(self, targets: list[tuple[str, str]], action: str):
        success, fail = 0, 0
        for pkg, name in targets:
            if action == "uninstall":
                _, out = run_adb("shell", "pm", "uninstall", "-k", "--user", "0", pkg)
                ok = "Success" in out
            else:
                _, out = run_adb("shell", "cmd", "package", "install-existing", pkg)
                ok = "install" in out.lower()
            if ok:
                self.after(0, self._log, f"  [OK] {name} ({pkg})")
                success += 1
            else:
                self.after(0, self._log, f"  [FAIL] {name} — {out}")
                fail += 1
        label = "제거" if action == "uninstall" else "복구"
        self.after(0, self._log, f"{label} 완료: {success}개 성공, {fail}개 실패")
        self.after(0, self._set_all_buttons, True)
        self.after(0, self._refresh_all)

    # ── 성능 적용/초기화 ────────────────────────────────

    def _on_perf_apply(self):
        selected = [s for s in PERFORMANCE_SETTINGS if self.perf_vars[s["key"]].get()]
        if not selected:
            self._log("적용할 항목이 없습니다")
            return
        self._set_all_buttons(False)
        self._log(f"{len(selected)}개 성능 설정 적용 시작...")
        threading.Thread(target=self._do_perf, args=(selected, "apply"), daemon=True).start()

    def _on_perf_reset(self):
        selected = [s for s in PERFORMANCE_SETTINGS if self.perf_vars[s["key"]].get()]
        if not selected:
            self._log("초기화할 항목이 없습니다")
            return
        self._set_all_buttons(False)
        self._log(f"{len(selected)}개 성능 설정 초기화 시작...")
        threading.Thread(target=self._do_perf, args=(selected, "reset"), daemon=True).start()

    def _do_perf(self, settings: list[dict], action: str):
        success = 0
        for s in settings:
            value = s["on_value"] if action == "apply" else s["off_value"]
            _, out = run_adb("shell", "settings", "put", s["namespace"], s["key"], value)
            self.after(0, self._log, f"  [OK] {s['name']} → {value}")
            success += 1
        label = "적용" if action == "apply" else "초기화"
        self.after(0, self._log, f"{label} 완료: {success}개")
        self.after(0, self._set_all_buttons, True)
        self.after(0, self._refresh_perf_status)


if __name__ == "__main__":
    app = App()
    app.mainloop()
