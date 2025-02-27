# level_sync_manager.py
from level_sync import LevelSyncSystem

class LevelSyncManager:
    def __init__(self, growth_system):
        self.level_sync_system = LevelSyncSystem(growth_system)
        self.pending_exp = {}  # レベルシンク中に獲得した経験値を保存
        
    def apply_level_sync(self, units, map_id):
        """マップ開始前のレベルシンク適用"""
        synced_units = self.level_sync_system.initialize_map(units, map_id)
        return synced_units
    
    def remove_level_sync(self, units):
        """マップ終了後のレベルシンク解除"""
        for unit in units:
            if unit.team == 0:  # プレイヤーユニットのみ
                self.level_sync_system.restore_original_stats(unit)
    
    def record_gained_exp(self, unit_name, exp):
        """レベルシンク中に獲得した経験値を記録"""
        if unit_name in self.pending_exp:
            self.pending_exp[unit_name] += exp
        else:
            self.pending_exp[unit_name] = exp
    
    def apply_pending_exp(self, units, growth_system):
        """記録された経験値を反映してレベルアップ処理"""
        level_up_results = {}
        
        for unit in units:
            if unit.name in self.pending_exp:
                exp_amount = self.pending_exp[unit.name]
                level_up, stat_gains = growth_system.award_exp(unit, exp_amount)
                
                if level_up:
                    level_up_results[unit.name] = stat_gains
                
                # 処理済みの経験値をクリア
                del self.pending_exp[unit.name]
        
        return level_up_results