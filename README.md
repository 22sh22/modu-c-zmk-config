# MODU-C ZMK Keymap Editor config (비공식)

MODU-C 원본 펌웨어를 직접 복사해 관리하는 대신, **원본 보드·실드·트랙볼 모듈은 고정된 upstream 커밋에서 받아오고 `config/modu.keymap`만 사용자 저장소에서 관리**하도록 만든 래퍼입니다.

이 저장소를 GitHub에 올리면 다음 흐름으로 사용할 수 있습니다.

1. ZMK Keymap Editor에서 `config/modu.keymap`을 그래픽으로 수정
2. 저장하면 Keymap Editor가 GitHub 저장소에 커밋
3. GitHub Actions가 좌·우 펌웨어를 빌드
4. Actions의 `modu-c-firmware` 아티팩트에서 `modu_left.uf2`, `modu_right.uf2` 다운로드

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
build.yaml
```

`.github`는 점으로 시작하지만 반드시 같이 올려야 합니다.

첫 업로드 직후 `Actions` 탭에서 `Build MODU-C ZMK firmware`가 실행됩니다. 성공한 실행을 열고 페이지 아래의 `Artifacts`에서 **`modu-c-firmware`**를 받습니다.

## 2. Keymap Editor에서 열기

1. `https://nickcoutsos.github.io/keymap-editor/`를 엽니다.
2. GitHub 연동으로 로그인하고 방금 만든 저장소를 선택합니다.
3. 키맵이 여러 개 보이면 `config/modu.keymap`을 선택합니다.
4. 수정 후 저장/커밋합니다.
5. 새 커밋이 들어오면 GitHub Actions가 자동으로 다시 빌드합니다.

Keymap Editor는 키맵 파일과 이름이 같은 `config/modu.json`을 우선 사용할 수 있고, 호환용으로 `config/info.json`도 동일하게 넣어 두었습니다.

## 3. 화면에 보이는 작은 `&none` 6칸

MODU-C 원본 펌웨어의 변환 행렬은 총 **67개 위치**입니다. 실제 바깥쪽 키 6개만 있는 다섯째 줄에도 가운데 좌표 6개가 존재하고, 원본 키맵에서는 이 좌표들이 `&none`으로 채워져 있습니다.

Keymap Editor가 바인딩 순서를 틀리지 않게 하려면 이 6개 좌표를 메타데이터에서도 빼면 안 됩니다. 그래서 화면 중앙에 아주 작은 칸으로 표시했습니다.

**그 작은 6칸은 그대로 `&none`으로 두세요.** 일반 키처럼 지정하면 실제 스위치와 연결되지 않거나 키 순서 관리가 헷갈릴 수 있습니다.

## 4. 펌웨어 받기와 플래시

Actions 성공 후 생성되는 최종 아티팩트:

```text
modu-c-firmware.zip
├─ modu_left.uf2
├─ modu_right.uf2
├─ LICENSE
├─ NOTICE.md
├─ THIRD_PARTY_NOTICES.md
└─ LICENSES/
```

각 파일은 이름이 같은 좌·우 절반에 사용합니다. 부트로더 진입과 UF2 복사는 MODU-C 제작자가 안내한 원래 방식대로 진행하세요.

원본 빌드 방식은 `ms88sf3/nrf52840` 보드로 양쪽을 각각 빌드한 뒤, 필요하면 nRF52840 UF2 family ID `0xADA52840`으로 HEX를 UF2로 변환합니다. 이 저장소의 워크플로도 같은 변환 방식을 자동화합니다.

## 5. 고정한 upstream 버전

재현 가능한 빌드를 위해 움직이는 `main` 대신 커밋을 고정했습니다.

- ZMK: `641514a97db345f499dd50b0360e594270f008fe`
- MODU-C 원본: `af7d209d8c2fe6c03ef38669f4114b69346ad31d`

원본이 갱신됐다고 이 값을 무작정 바꾸면 ZMK·Zephyr·트랙볼 드라이버 호환성이 깨질 수 있습니다.

## 6. 검증 범위

로컬 정적 검증은 다음을 확인합니다.

- `modu.json`과 `info.json` 일치
- 원본 행렬 순서와 동일한 67개 좌표
- 기본/Lower 레이어 각각 67개 바인딩
- 기본 레이어의 `&none` 6개 유지
- 좌·우 빌드 대상, 두 커스텀 모듈, UF2 변환 설정 존재

직접 실행:

```bash
python3 scripts/validate.py
```

단, 이 패키지를 만든 환경에서는 전체 ZMK 툴체인과 실제 MODU-C 하드웨어를 사용할 수 없어 **GitHub Actions의 실제 컴파일과 실기 플래시는 아직 수행하지 않았습니다.** 첫 Actions 실행이 통합 빌드 검증입니다.

## 라이선스와 표시

이 저장소는 EKS Inc. 또는 MODU의 공식 배포물이 아닌 **비공식 수정본**입니다. 원본 MODU 전용 코드와 키맵은 `EKS NON-COMMERCIAL SOURCE LICENSE 1.0`의 적용을 받으며 비상업적 용도로만 사용할 수 있습니다.

개인 키보드용 사용·수정과 비상업적 공개 재배포는 허용되지만, 판매 제품에 넣거나 유료 키맵/펌웨어 서비스를 제공하는 등 상업적 사용은 EKS Inc.의 사전 서면 허가가 필요합니다. GitHub에 올릴 때 `LICENSE`, `NOTICE.md`, `THIRD_PARTY_NOTICES.md`, `LICENSES/`와 키맵 상단의 저작권·수정 표시를 삭제하지 마세요. 빌드 아티팩트에도 같은 고지 파일이 자동 포함됩니다.

자세한 조건은 `LICENSE`, `NOTICE.md`, `THIRD_PARTY_NOTICES.md`를 확인하세요.
