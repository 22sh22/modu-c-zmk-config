# MODU-C ZMK Keymap Editor config (비공식)

MODU-C 원본 펌웨어 전체를 복사해 따로 관리하는 대신, **원본 보드·실드·트랙볼 모듈은 고정된 upstream 커밋에서 받아오고 `config/modu.keymap`만 사용자 저장소에서 관리**하도록 만든 비공식 래퍼입니다.

이 버전은 2026-09-02에 키맵 좌표, 빌드 행렬, west 모듈, GitHub Actions, HEX→UF2 변환, 라이선스 고지를 다시 점검하고 안전 검사를 보강한 감사본입니다.

사용 흐름은 다음과 같습니다.

1. ZMK Keymap Editor에서 `config/modu.keymap`을 그래픽으로 수정
2. Keymap Editor가 GitHub 저장소에 변경사항을 커밋
3. GitHub Actions가 정적 검사와 도구 자체 테스트를 실행
4. ZMK 공식 재사용 워크플로가 좌·우 펌웨어를 각각 빌드
5. 최종 작업이 정확한 두 결과물만 선택하고 UF2 구조를 검사
6. `modu-c-firmware` 아티팩트에서 `modu_left.uf2`, `modu_right.uf2` 다운로드

## 1. GitHub에 올리기

1. GitHub에서 빈 저장소를 하나 만듭니다. 이름은 예를 들어 `modu-c-zmk-config`로 하면 됩니다.
2. 이 ZIP을 압축 해제합니다.
3. **압축을 푼 바깥 폴더 자체가 아니라, 그 안의 파일과 폴더 전체**를 저장소 루트에 올립니다.
4. 저장소 최상단에서 아래 구조가 보이면 정상입니다.

```text
.github/workflows/build.yml
config/modu.keymap
config/modu.json
config/info.json
config/west.yml
scripts/validate.py
scripts/selftest.py
scripts/normalize_hex.py
scripts/package_firmware.py
scripts/verify_uf2.py
build.yaml
```

`.github`는 점으로 시작하지만 반드시 같이 올려야 합니다.

첫 업로드 직후 `Actions` 탭에서 **Build MODU-C ZMK firmware**가 실행됩니다. 성공한 실행을 열고 페이지 아래 `Artifacts`에서 **modu-c-firmware**를 받습니다.

## 2. Keymap Editor에서 열기

1. ZMK Keymap Editor를 엽니다.
2. GitHub 연동으로 로그인하고 방금 만든 저장소를 선택합니다.
3. 키맵이 여러 개 보이면 `config/modu.keymap`을 선택합니다.
4. 수정 후 저장/커밋합니다.
5. 새 커밋이 들어오면 GitHub Actions가 자동으로 다시 빌드합니다.

Keymap Editor는 키맵 파일과 이름이 같은 `config/modu.json`을 사용할 수 있고, 호환용으로 `config/info.json`도 동일하게 넣어 두었습니다.

## 3. 화면에 보이는 작은 6칸

MODU-C 원본 변환 행렬은 총 **67개 위치**입니다. 실제 바깥쪽 키 6개만 있는 다섯째 줄에도 가운데 행렬 좌표 6개가 존재하고, 원본 기본 레이어에서는 이 좌표들이 `&none`으로 채워져 있습니다.

Keymap Editor가 바인딩 순서를 틀리지 않게 하려면 메타데이터에서도 이 6개 좌표를 빼면 안 됩니다. 그래서 화면 중앙에 아주 작은 칸으로 표시했습니다.

**작은 6칸은 기본 레이어에서 그대로 `&none`으로 두세요.** 자동 검사는 이들이 정확히 0부터 세었을 때 51–56번 위치에 있는지도 확인합니다.

## 4. Actions에서 정상적으로 보여야 하는 단계

한 번의 실행 안에서 다음 세 작업이 모두 초록색이어야 합니다.

```text
Validate Keymap Editor and packaging files
Build both halves
Package and verify flashable UF2 files
```

첫 작업은 좌표·바인딩·빌드 설정을 검사하고, 가짜 HEX/UF2 자료로 성공·실패 경로를 자체 시험합니다. 두 번째 작업은 `modu_left`와 `modu_right`를 실제 ZMK로 빌드합니다. 마지막 작업은 이름이 정확히 일치하는 좌우 결과물만 선택하고 최종 UF2를 다시 검사합니다.

어느 단계라도 빨간색이면 그 실행에서 나온 UF2는 사용하지 마세요.

## 5. 펌웨어와 플래시

최종 아티팩트는 다음과 같은 형태입니다.

```text
modu-c-firmware.zip
├─ modu_left.uf2
├─ modu_right.uf2
├─ LICENSE
├─ NOTICE.md
├─ THIRD_PARTY_NOTICES.md
└─ LICENSES/
```

파일 이름이 같은 좌·우 절반에 각각 사용합니다. 부트로더 진입과 UF2 복사는 MODU-C 제작자가 안내한 원래 방식대로 진행하세요.

원본 빌드 방식은 `ms88sf3/nrf52840` 보드로 `modu_left`와 `modu_right`를 각각 빌드한 뒤, 필요하면 nRF52840 UF2 family ID `0xADA52840`으로 HEX를 UF2로 변환합니다. 이 저장소도 동일한 보드·실드명과 family ID를 사용합니다.

## 6. 고정한 upstream 소스

갑자기 움직이는 브랜치를 따라가다 호환성이 깨지는 일을 줄이기 위해 소스 리비전을 고정했습니다.

- ZMK: `641514a97db345f499dd50b0360e594270f008fe`
- MODU-C 원본: `af7d209d8c2fe6c03ef38669f4114b69346ad31d`

이는 ZMK와 MODU-C **소스 버전**을 고정한다는 뜻입니다. GitHub 호스티드 러너와 ZMK 공식 빌드 컨테이너는 서비스 측에서 갱신될 수 있으므로, 모든 시점에 바이트 단위로 완전히 동일한 빌드를 보장한다는 뜻은 아닙니다.

## 7. 자동 안전장치

`python3 scripts/validate.py`는 다음을 확인합니다.

- 두 레이아웃 JSON의 일치와 중복 JSON 키
- 원본 행렬과 같은 67개 좌표 및 순서
- 모든 키맵 레이어의 67개 바인딩
- 기본 레이어 중앙 `&none`의 정확한 위치
- 좌·우 보드/실드/아티팩트 이름
- 두 추가 모듈 경로와 CMake 인수 인용
- 고정된 ZMK·MODU-C 커밋
- Actions의 변환·검증·라이선스 포함 단계

`python3 scripts/selftest.py`는 다음을 실제 임시 파일로 시험합니다.

- 정상/손상 Intel HEX 판별(체크섬·문자·레코드 주소·16비트 경계)
- CRLF와 마지막 빈 줄 제거
- native UF2 경로와 HEX 변환 경로
- 좌·우 파일 누락 및 중복 탐지
- UF2 magic, 블록 번호, 주소 정렬·겹침·32비트 범위, family ID
- 좌·우 결과물이 실수로 같은 파일인지 여부

최종 패키징은 원본 변환기에 HEX를 넘기기 전에 기록 길이와 체크섬을 검사하고 마지막 빈 줄이 없는 형태로 정규화합니다. 변환 후에는 UF2가 512바이트 블록 구조인지, family ID가 `0xADA52840`인지, 블록 번호·주소가 모순되지 않는지 확인합니다.

더 자세한 점검 내용은 `VALIDATION.md`에 있습니다.

## 8. 확인되지 않은 마지막 범위

이 ZIP을 만든 환경에서는 완전한 ZMK/Zephyr 툴체인과 실제 MODU-C 하드웨어를 사용할 수 없어 다음은 직접 실행하지 못했습니다.

- 전체 `west update`와 실제 펌웨어 컴파일
- GitHub 호스티드 재사용 워크플로 실행
- 실제 키보드에 플래시한 뒤 키스캔·Bluetooth·LED·양쪽 트랙볼 확인

따라서 **첫 GitHub Actions 전체 성공이 컴파일 통합 검증**이고, **실제 키보드 플래시가 하드웨어 최종 검증**입니다. 정적 검사만 한 이전 상태보다 실패 가능성을 크게 줄였지만, 실제 빌드와 기기 테스트 전에는 100% 작동을 보증할 수 없습니다.

## 라이선스와 표시

이 저장소는 EKS Inc. 또는 MODU의 공식 배포물이 아닌 **비공식 수정본**입니다. 원본 MODU 전용 코드와 키맵은 `EKS NON-COMMERCIAL SOURCE LICENSE 1.0`의 적용을 받으며 비상업적 용도로만 사용할 수 있습니다.

개인 키보드용 사용·수정과 비상업적 공개 재배포는 허용되지만, 판매 제품에 넣거나 유료 키맵/펌웨어 서비스를 제공하는 등 상업적 사용은 EKS Inc.의 사전 서면 허가가 필요합니다. GitHub에 올릴 때 `LICENSE`, `NOTICE.md`, `THIRD_PARTY_NOTICES.md`, `LICENSES/`와 키맵 상단의 저작권·수정 표시를 삭제하지 마세요. 빌드 아티팩트에도 같은 고지 파일이 자동 포함됩니다.
