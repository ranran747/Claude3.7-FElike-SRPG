# save_system.py
import json
import os
import datetime

class SaveSystem:
    def __init__(self, save_directory="saves"):
        self.save_directory = save_directory
        os.makedirs(save_directory, exist_ok=True)
    
    def save_game(self, slot, game_data):
        """ゲームデータをセーブ"""
        save_path = os.path.join(self.save_directory, f"save_{slot}.json")
        
        # セーブデータに日時を追加
        save_data = game_data.copy()
        save_data["save_time"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        try:
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"セーブエラー: {e}")
            return False
    
    def load_game(self, slot):
        """セーブデータをロード"""
        save_path = os.path.join(self.save_directory, f"save_{slot}.json")
        
        if not os.path.exists(save_path):
            return None
        
        try:
            with open(save_path, 'r', encoding='utf-8') as f:
                save_data = json.load(f)
            return save_data
        except Exception as e:
            print(f"ロードエラー: {e}")
            return None
    
    def get_save_info(self, slot):
        """セーブデータの基本情報を取得"""
        save_path = os.path.join(self.save_directory, f"save_{slot}.json")
        
        if not os.path.exists(save_path):
            return None
        
        try:
            with open(save_path, 'r', encoding='utf-8') as f:
                save_data = json.load(f)
            
            # 基本情報のみ抽出
            info = {
                "save_time": save_data.get("save_time", "不明"),
                "party": save_data.get("party", []),
                "play_time": save_data.get("play_time", 0),
                "gold": save_data.get("gold", 0),
                "current_scenario": save_data.get("current_scenario", "")
            }
            return info
        except Exception as e:
            print(f"セーブ情報取得エラー: {e}")
            return None
    
    def get_all_saves(self):
        """全セーブデータの情報を取得"""
        saves = {}
        
        for i in range(1, 10):  # 9つのセーブスロット
            info = self.get_save_info(i)
            if info:
                saves[i] = info
        
        return saves