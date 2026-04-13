# Y700 Cleaner

Lenovo Legion Y700 블로트웨어 제거 + 최적화 도구 (GUI)

기기를 자동 감지하여 맞춤 목록을 표시합니다.

![Windows](https://img.shields.io/badge/Windows-11-blue) ![Python](https://img.shields.io/badge/Python-3.11+-green) ![License](https://img.shields.io/badge/License-MIT-yellow)

## 지원 기기

| 항목 | Lenovo Legion Y700 (3세대) |
|---|---|
| 코드명 | TB322FC |
| 펌웨어 | ZUI ZUXOS 1.5.x |
| Android | 16 (API 36) |
| 플랫폼 | Qualcomm sun |
| 리전 | CN_OPEN (중국 내수판) |

> **주의**: 이 도구는 CN_OPEN ROM 기준으로 패키지 목록을 구성했습니다.
> GL/Global ROM 은 일부 패키지명이 다를 수 있으며, 그 경우 설치되지 않은 항목은 목록에서 자동으로 숨겨집니다.

## 기능

- 기기 자동 감지 — USB 연결 시 모델을 자동 인식
- 블로트웨어 카테고리별 분류 및 선택 제거/복구
- USB 연결 상태 실시간 모니터링 (3초 폴링)
- 실시간 작업 로그
- ZUI 런처/코어/키보드/HyperEngine/Dolby 자동 보호 (KEEP_PACKAGES)
- 성능 최적화 (애니메이션 0.5배, 백그라운드 스캔 중지 등)

## 제거 대상

- **Baidu / 중국 트래커** — Baidu 위치추적
- **Lenovo CN 서비스** — Lenovo 앱스토어, 클라우드 동기화, 계정(xbb), 날씨, Tianjiao 교육 등
- **Lenovo 푸시/광고** — 새로운 기능 알림, 푸시 광고, Xiaotian 트리거
- **Lenovo 음성/원격지원** — Lenovo Voice, LeVision, LMSA
- **공장/엔지니어링 테스트** — EngineeringCode, 공장 테스트, Lenovo 자동설치
- **ZUI 선택 앱** — ZUI 브라우저, AI 렌즈/스타일러스, PP, xlog 등
- **WAPI** — 중국 WiFi 인증서 관리자
- **Android 불필요 앱** — 인쇄, HTML 뷰어, SMS/MMS, 웹캠 모드, 긴급재난문자 등
- **Qualcomm XR/부가** — XR WiFi/비디오, 음성 핫워드, 위성 통신
- **SIM/통신** — eSIM, SIM 관련 (Y700 은 WiFi-only)

## 유지 권장 (제거 금지)

다음 패키지는 `KEEP_PACKAGES` 목록에 등록되어 목록에 나오지 않습니다.

| 분류 | 패키지 |
|---|---|
| 런처/코어 | `com.zui.launcher`, `com.zui.desktoplauncher`, `com.zui.cores`, `com.zui.engine`, `com.zui.resolver`, `com.zui.setupwizard` |
| 설정/UI | `com.zui.safecenter`, `com.zui.homesettings`, `com.zui.themes.provider`, `com.zui.dynamic.color.overlay` |
| 키보드/기기 | `com.zui.keyboardupdate.olympia`, `com.zui.deviceidservice` |
| 생산성 | `com.zui.freeform.sidebar`, `com.zui.filemanager`, `com.zui.camera`, `com.zui.gallery` |
| 게이밍 | `com.lenovo.hyperengine`, `com.lenovo.tab_extreme`, `com.lenovo.tbengine` |
| 스타일러스/분할 | `com.lenovo.penservice`, `com.lenovo.screensplit` |
| PC 모드 | `com.motorola.mobiledesktop.core` |
| 미디어 | `com.dolby.daxservice`, `com.dolby.dolbyvisionservice` |

## 다운로드

[Releases](../../releases) 페이지에서 최신 zip을 다운로드하세요.

Python 설치 불필요 — exe + ADB가 포함되어 있습니다.

## 사용법

### 사전 준비: USB 디버깅 활성화

1. 설정 > 태블릿 정보 > **빌드 번호** 7회 탭 → "개발자가 되셨습니다"
2. 설정 > 시스템 > 개발자 옵션 > **USB 디버깅** 켜기
3. USB 케이블로 PC 연결 → 태블릿 화면의 "USB 디버깅 허용" 팝업에서 **허용**

### 프로그램 실행

1. zip 압축 해제
2. USB 케이블로 PC에 연결 (USB 디버깅 활성화 상태)
3. `Y700Cleaner.exe` 실행 — 기기가 자동 감지됨
4. "앱 제거" 탭에서 앱 선택 후 "선택 앱 제거" 클릭
5. "성능 최적화" 탭에서 항목 선택 후 "선택 항목 적용"

### 복구

- 프로그램 내 "선택 앱 복구" 버튼 사용
- 또는 공장초기화 시 자동 복구됨
- 수동: `adb shell cmd package install-existing <패키지명>`

### CLI 모드

```
py y700_cleaner.py              # 대화형 모드
py y700_cleaner.py --list       # 제거 대상 목록만 출력
py y700_cleaner.py --clean      # 전체 제거 실행
py y700_cleaner.py --restore    # 복구
py y700_cleaner.py --perf       # 성능 설정 적용
py y700_cleaner.py --perf-reset # 성능 설정 초기화
```

## 제거 방식

```
adb shell pm uninstall -k --user 0 <패키지명>
```

사용자 레벨에서만 제거되며, 시스템 파티션은 건드리지 않습니다.
공장초기화(Factory Reset) 시 모든 앱이 자동 복구됩니다.

## 빌드 (개발자용)

```
py -m pip install customtkinter pyinstaller
py -m PyInstaller Y700Cleaner.spec --clean --noconfirm
```

`dist/Y700Cleaner.exe` 생성됨.

## 폴더 구조

```
Y700Cleaner/
├── Y700Cleaner.exe          # GUI 프로그램
├── platform-tools/           # ADB 동봉
│   ├── adb.exe
│   ├── AdbWinApi.dll
│   └── AdbWinUsbApi.dll
└── README.txt                # 사용법
```

## 안전성 원칙

`boox-cleaner` 프로젝트의 v2.2 사건 (kreader 제거 → ContentProvider 의존성 → 부팅 크래시) 교훈을 반영했습니다.

- 모든 작업은 사용자 레벨 (`--user 0`) 에서만 수행
- 런처/코어/키보드/게이밍 엔진/PC 모드는 `KEEP_PACKAGES` 로 보호
- 용도가 불명한 패키지는 기본 목록에 포함하지 않음
- 공장초기화 시 모든 변경이 자동 복구됨

## License

MIT
