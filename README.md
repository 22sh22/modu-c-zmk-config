# MODU-C ZMK Keymap Editor config (User customed)

MODU-C 원본 펌웨어 전체를 복사하는 대신, 일부 파일을 불러와 keymap editor, github actions를 사용할 수 있게 만든 레포지토리입니다.

`main` 브랜치를 fork 한 후, 해당 레포지토리를 [keymap editor](https://nickcoutsos.github.io/keymap-editor/) 로 불러와 수정하십시오.

## ZMK Studio 테스트 (`studio-test` 브랜치)

이 브랜치는 왼쪽 central에 ZMK Studio를 활성화한 테스트 버전입니다.
Actions에서 **이 브랜치의 성공한 실행**을 선택하고 `modu-c-firmware` 아티팩트의
좌우 UF2를 해당 기기에 설치한 뒤, 왼쪽을 USB 데이터 케이블로 연결하십시오.

- 기본 키맵의 Fn(엄지 `MO1`)을 누른 채 `T`: USB 출력 선택
- [ZMK Studio](https://zmk.studio/)에서 연결한 뒤 Fn+`R`: 잠금 해제
- Fn+`G`: BLE 출력 선택

세부 절차, 저장/복원 동작 및 실기기 확인 항목은 [Studio 테스트 안내](docs/STUDIO_TEST.md)를 참고하십시오.
기존 67개 논리 위치와 썸클러스터 방향 보정, 양쪽 트랙볼 설정은 유지합니다.
실기기 동작 검증 전의 테스트 펌웨어입니다.

## 라이선스와 표시

이 저장소의 원본 MODU 전용 코드와 키맵은 `EKS NON-COMMERCIAL SOURCE LICENSE 1.0`의 적용을 받으며 비상업적 용도로만 사용할 수 있습니다.
