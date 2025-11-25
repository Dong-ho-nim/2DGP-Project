from players.base import BasePlayer


class Byakuya(BasePlayer):
    def __init__(self, x=640, y=400, sheet_path=None, animations=None, default_anim="Idle"):
        # 기본 스프라이트 시트 경로와 Idle 애니메이션 파라미터
        # 존재하는 파일명으로 수정
        sheet = sheet_path or "DS _ DSi - Bleach_ Dark Souls - Characters - Byakuya Kuchiki.png"
        anims = animations or {
            "Idle": {"row": 2, "w": 66, "h": 108, "cols": 8, "fps": 8},
        }
        super().__init__(x, y, sheet, anims, default_anim)
