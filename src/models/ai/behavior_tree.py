from enum import Enum
import time
import random
from typing import Callable, List, Dict, Any, Optional

class NodeStatus(Enum):
    """Davranış ağacı düğümünün çalışma durumu"""
    SUCCESS = 1    # Başarılı
    FAILURE = 2    # Başarısız
    RUNNING = 3    # Çalışıyor

class BehaviorNode:
    """Davranış ağacındaki temel düğüm"""
    def __init__(self, name: str):
        self.name = name
        self.parent = None
        self.children: List[BehaviorNode] = []
        
    def add_child(self, child: 'BehaviorNode') -> 'BehaviorNode':
        """Düğüme alt düğüm ekle"""
        self.children.append(child)
        child.parent = self
        return child
    
    def run(self, villager, dt: float) -> NodeStatus:
        """Düğümü çalıştır"""
        raise NotImplementedError("Bu metot alt sınıflar tarafından uygulanmalıdır")
    
    def __str__(self) -> str:
        return f"{self.name} ({self.__class__.__name__})"

class SequenceNode(BehaviorNode):
    """Sırayla tüm alt görevleri yapmaya çalışan düğüm.
    Tüm alt düğümler başarılı olursa SUCCESS, biri başarısız olursa FAILURE döner."""
    def run(self, villager, dt: float) -> NodeStatus:
        for child in self.children:
            status = child.run(villager, dt)
            
            if status == NodeStatus.FAILURE:
                return NodeStatus.FAILURE
            
            if status == NodeStatus.RUNNING:
                return NodeStatus.RUNNING
        
        return NodeStatus.SUCCESS if self.children else NodeStatus.FAILURE

class SelectorNode(BehaviorNode):
    """Alt görevlerden birini yapmaya çalışan düğüm.
    Bir alt düğüm başarılı olursa SUCCESS, hiçbiri başarılı olmazsa FAILURE döner."""
    def run(self, villager, dt: float) -> NodeStatus:
        for child in self.children:
            status = child.run(villager, dt)
            
            if status == NodeStatus.SUCCESS:
                return NodeStatus.SUCCESS
            
            if status == NodeStatus.RUNNING:
                return NodeStatus.RUNNING
        
        return NodeStatus.FAILURE

class ActionNode(BehaviorNode):
    """Belirli bir eylemi gerçekleştiren düğüm"""
    def __init__(self, name: str, action_func: Callable[[Any, float], NodeStatus]):
        super().__init__(name)
        self.action_func = action_func
    
    def run(self, villager, dt: float) -> NodeStatus:
        try:
            return self.action_func(villager, dt)
        except Exception as e:
            print(f"HATA: {self.name} eylem düğümü çalıştırma hatası: {e}")
            import traceback
            traceback.print_exc()
            return NodeStatus.FAILURE

class ConditionNode(BehaviorNode):
    """Bir koşulu kontrol eden düğüm"""
    def __init__(self, name: str, condition_func: Callable[[Any, float], bool]):
        super().__init__(name)
        self.condition_func = condition_func
    
    def run(self, villager, dt: float) -> NodeStatus:
        try:
            result = self.condition_func(villager, dt)
            return NodeStatus.SUCCESS if result else NodeStatus.FAILURE
        except Exception as e:
            print(f"HATA: {self.name} koşul düğümü çalıştırma hatası: {e}")
            import traceback
            traceback.print_exc()
            return NodeStatus.FAILURE

class InverterNode(BehaviorNode):
    """Alt düğümün sonucunu tersine çeviren düğüm"""
    def run(self, villager, dt: float) -> NodeStatus:
        if not self.children:
            return NodeStatus.FAILURE
        
        status = self.children[0].run(villager, dt)
        
        if status == NodeStatus.SUCCESS:
            return NodeStatus.FAILURE
        elif status == NodeStatus.FAILURE:
            return NodeStatus.SUCCESS
        
        return status

class RepeatUntilFailureNode(BehaviorNode):
    """Alt düğümü başarısız olana kadar tekrarlayan düğüm"""
    def run(self, villager, dt: float) -> NodeStatus:
        if not self.children:
            return NodeStatus.FAILURE
        
        status = self.children[0].run(villager, dt)
        
        if status == NodeStatus.FAILURE:
            return NodeStatus.SUCCESS
        
        return NodeStatus.RUNNING

class RandomSelectorNode(SelectorNode):
    """Alt düğümlerden rastgele birini seçen düğüm"""
    def run(self, villager, dt: float) -> NodeStatus:
        if not self.children:
            return NodeStatus.FAILURE
        
        # Rastgele bir alt düğüm seç
        child = random.choice(self.children)
        return child.run(villager, dt)

class ParallelNode(BehaviorNode):
    """Tüm alt düğümleri paralel çalıştıran düğüm.
    Başarı/başarısızlık politikası parametreyle belirlenir."""
    def __init__(self, name: str, success_threshold: int = None, failure_threshold: int = None):
        super().__init__(name)
        # None ise tüm çocuklar başarılı olmalı
        self.success_threshold = success_threshold 
        # None ise herhangi bir çocuk başarısız olursa başarısız
        self.failure_threshold = failure_threshold
    
    def run(self, villager, dt: float) -> NodeStatus:
        if not self.children:
            return NodeStatus.FAILURE
        
        success_count = 0
        failure_count = 0
        
        for child in self.children:
            status = child.run(villager, dt)
            
            if status == NodeStatus.SUCCESS:
                success_count += 1
            elif status == NodeStatus.FAILURE:
                failure_count += 1
        
        # Başarı/başarısızlık eşiklerini kontrol et
        success_threshold = self.success_threshold if self.success_threshold is not None else len(self.children)
        failure_threshold = self.failure_threshold if self.failure_threshold is not None else 1
        
        if success_count >= success_threshold:
            return NodeStatus.SUCCESS
        
        if failure_count >= failure_threshold:
            return NodeStatus.FAILURE
        
        return NodeStatus.RUNNING

class DelayNode(BehaviorNode):
    """Belirli bir süre bekleyen düğüm"""
    def __init__(self, name: str, delay_seconds: float):
        super().__init__(name)
        self.delay_seconds = delay_seconds
        self.start_time = None
    
    def run(self, villager, dt: float) -> NodeStatus:
        current_time = time.time()
        
        if self.start_time is None:
            self.start_time = current_time
        
        # Süre doldu mu kontrol et
        if current_time - self.start_time >= self.delay_seconds:
            self.start_time = None
            return NodeStatus.SUCCESS
        
        return NodeStatus.RUNNING

class BlackboardNode(BehaviorNode):
    """Villager'ın durumunu bir kara tahta gibi kullanarak veri saklar ve okur"""
    @staticmethod
    def set_data(villager, key: str, value: Any) -> None:
        if not hasattr(villager, '_blackboard'):
            villager._blackboard = {}
        villager._blackboard[key] = value
    
    @staticmethod
    def get_data(villager, key: str, default: Any = None) -> Any:
        if not hasattr(villager, '_blackboard'):
            return default
        return villager._blackboard.get(key, default)
    
    @staticmethod
    def clear_data(villager, key: str) -> None:
        if hasattr(villager, '_blackboard') and key in villager._blackboard:
            del villager._blackboard[key] 