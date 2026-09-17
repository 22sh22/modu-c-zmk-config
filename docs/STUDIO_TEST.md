# MODU-C ZMK Studio 테스트

대상: `studio-test` 브랜치. 실기기 검증이 필요한 테스트 펌웨어입니다.

## 변경 범위

- 왼쪽 `modu_left` central에 `CONFIG_ZMK_STUDIO=y`와 `studio-rpc-usb-uart`를 적용합니다.
- 오른쪽 `modu_right`에는 Studio RPC를 활성화하지 않습니다.
- `config/modu-layouts.dtsi`에서 기존 JSON의 67개 위치를 Studio 물리 배치로 제공합니다.
- 물리 배치는 기존 `default_transform`과 `alt_thumb_kscan`을 참조합니다.
  오른쪽 열 오프셋 및 P0.08 기반 부팅 시 썸클러스터 방향 보정은 유지합니다.
- 51~56번의 작은 여섯 자리표시자도 유지합니다. 실제 키처럼 설정하지 마십시오.
- 기존 세 레이어, 양쪽 트랙볼, LED 및 배터리 설정을 유지합니다.
- ZMK `641514a97db345f499dd50b0360e594270f008fe`와 MODU 펌웨어
  `bee0bb4b812f63f279eb67e928accc89600b5904` 고정 버전을 유지합니다.

## 빌드 및 설치

1. GitHub Actions의 **Build MODU-C ZMK firmware**에서 `studio-test` 브랜치 실행을 선택합니다.
   필요하면 **Run workflow**에서 해당 브랜치를 지정합니다.
2. 검증, 좌우 컴파일, UF2 패키징까지 모두 성공한 실행의 `modu-c-firmware` 아티팩트를 받습니다.
3. 기존 펌웨어와 사용자 키맵은 복귀할 수 있도록 별도로 보관합니다.
4. 평소 사용하던 UF2 부트로더 진입 절차로 각각 설치합니다.
   - 왼쪽: `modu_left.uf2`
   - 오른쪽: `modu_right.uf2`
5. 양쪽 전원을 다시 켜고, 왼쪽을 PC에 USB 데이터 케이블로 연결합니다.

## 첫 연결과 키 변경

다음 단축키는 이 브랜치의 **기본 키맵** 기준입니다.
엄지 `MO1`로 layer 1을 누른 상태에서 왼쪽 Ctrl 위치의 키를 누르고 T 또는 R을 누릅니다.
이는 기존 5/6 부트로더 키와 같은 접근 방식입니다. layer 1의 왼쪽 Ctrl은
`&mo 2`로 기존 `layer_2`에 접근하며, PC에 Ctrl 수정자를 보내는 동작이 아닙니다.

| 동작 | 키 |
|---|---|
| USB 출력 선택 | `layer 1 + 왼쪽 Ctrl + T` |
| Studio 잠금 해제 | `layer 1 + 왼쪽 Ctrl + R` |

1. `layer 1 + 왼쪽 Ctrl + T`로 USB 출력을 선택합니다. USB와 BLE가 동시에 연결된 경우에도 Studio 연결과 출력 경로가 일치하도록 합니다.
2. PC의 Chrome/Edge에서 <https://zmk.studio/>에 접속하고 USB/Serial 연결에서 MODU 장치를 선택합니다.
   오른쪽은 Studio 연결 대상이 아닙니다.
3. 연결 후 `layer 1 + 왼쪽 Ctrl + R`을 눌러 잠금을 해제합니다. 잠금 보호는 활성 상태로 유지합니다.
4. 시험할 키 하나를 변경하고 Studio에서 저장합니다.
5. 실제 입력과 양쪽 키의 변경 반영 여부를 확인합니다.
6. 전원을 껐다 켜고 변경 내용이 유지되는지 확인합니다.

BLE 연결 시험은 USB 시험을 마친 후 진행하십시오. Windows/macOS에서는 Studio 네이티브 앱을 사용합니다.

## 저장과 복원

- Studio에서 저장한 키맵은 기기 설정 영역에 저장됩니다. GitHub의 `.keymap` 파일은 자동으로 변경되지 않습니다.
- 이후 `.keymap`을 수정해 새 펌웨어를 올려도 저장된 Studio 키맵이 우선할 수 있습니다.
- 새 펌웨어의 기본 키맵을 적용하려면 Studio의 **Restore Stock Settings**를 사용합니다.
  이 작업은 Studio 키맵 변경을 초기화하므로 필요한 설정을 먼저 기록하십시오.
- 잠금 해제 키와 layer 1 + 왼쪽 Ctrl 접근 경로를 모두 다른 기능으로 바꾸지 마십시오.
- 기존 펌웨어로 돌아갈 때는 보관한 좌우 UF2를 각 기기에 다시 설치합니다.
  Studio에 저장한 설정이 플래싱만으로 삭제된다고 가정하지 마십시오.
  이후 Studio 펌웨어를 다시 시험하면 기존 저장 키맵이 나타날 수 있습니다.
- 일반 설치에서 BLE 페어링 초기화는 요구하지 않습니다. 연결 문제가 생기면 증상과 로그를 확인한 뒤 별도로 처리합니다.

## 실기기 확인 항목

- [ ] USB에서 Studio 장치가 검색되고 `layer 1 + 왼쪽 Ctrl + R`로 잠금 해제됨
- [ ] 왼쪽과 오른쪽 키의 변경이 모두 반영됨
- [ ] 모든 실제 키가 화면에서 의도한 위치와 대응함
- [ ] 저장 후 전원 재인가에도 변경 내용이 유지됨
- [ ] P0.08 선택 상태별로 재부팅 후 썸클러스터 방향이 기존과 동일하게 동작함
- [ ] 양쪽 트랙볼 이동 및 마우스 버튼 동작이 유지됨
- [ ] USB/BLE 출력 전환 및 좌우 재연결이 정상임
- [ ] 절전 복귀 후 키 입력과 트랙볼이 정상임
- [ ] Restore Stock Settings로 기본 키맵과 테스트 단축키가 복원됨

Studio는 이번 구성에서 키맵 편집을 제공합니다. 트랙볼 CPI/회전 설정,
새 매크로/콤보 정의, 좌우 central 역할 변경 및 모듈 자동 감지는 별도 펌웨어 작업입니다.

## 개발 검증

```sh
python3 scripts/validate.py
python3 scripts/test_validate.py
python3 scripts/selftest.py
```

CI 컴파일 성공은 실기기 검증을 대신하지 않습니다.
기존 `VALIDATION.md`는 2026-09-02 기본 브랜치 감사 기록이며, Studio 실기기 검증 결과가 아닙니다.

공식 참고: [Studio](https://zmk.dev/docs/features/studio),
[물리 배치](https://zmk.dev/docs/hardware-integration/physical-layouts).
