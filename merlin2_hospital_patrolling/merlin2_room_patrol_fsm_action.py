# TODO: write the patrol FSM action

from typing import List
import rclpy

from .pddl import room_type, room_at, room_patrolled

from merlin2_basic_actions.merlin2_basic_types import wp_type
from merlin2_basic_actions.merlin2_basic_predicates import robot_at

from merlin2_fsm_action import (
    Merlin2FsmAction,
    Merlin2BasicStates
)

from yasmin_ros.basic_outcomes import SUCCEED
from yasmin import CbState
from yasmin.blackboard import Blackboard

from kant_dto import (
    PddlObjectDto,
    PddlConditionEffectDto,
)

class Merlin2RoomPatrolFsmAction(Merlin2FsmAction):

    def __init__(self):

        self._room = PddlObjectDto(room_type, "room")
        self._wp = PddlObjectDto(wp_type, "wp")

        super().__init__("room_patrol")

        tts_state = self.create_state(Merlin2BasicStates.TTS)

        self.add_state(
            "PREPARING_TEXT",
            CbState([SUCCEED], self.prepare_text),
            transitions={SUCCEED: "SPEAKING"},
        )

        self.add_state(
            "SPEAKING",
            tts_state,
        )

        rotation_state = self.create_state(Merlin2BasicStates.NAVIGATION) # STT

        self.add_state(
            "PREPARING_ROTATION",
            CbState([SUCCEED], self.rotate),
            transitions={SUCCEED: "ROTATING"},
        )

        self.add_state(
            "ROTATING",
            rotation_state,
        )

    def rotate(self, blackboard: Blackboard) -> str:
        blackboard.twist.angular.z = 0.5
        blackboard.twist.angular.z = 0
        return SUCCEED

    def prepare_text(self, blackboard: Blackboard) -> str:
        # room_name = blackboard.merlin2_action_goal.objects[0][-1]
        blackboard.text = "I am patrolling the room"
        return SUCCEED
    
    def create_parameters(self) -> List[PddlObjectDto]:
        return [self._room, self._wp]
    
    def create_conditions(self) -> List[PddlConditionEffectDto]:
        
        cond_1 = PddlConditionEffectDto(
            room_patrolled,
            [self._room],
            PddlConditionEffectDto.AT_START,
            is_negative=False
        )

        cond_2 = PddlConditionEffectDto(
            room_at,
            [self._wp],
            PddlConditionEffectDto.AT_START
        )

        cond_3 = PddlConditionEffectDto(
            room_at,
            [self._room, self._wp],
            PddlConditionEffectDto.AT_START
        )

        return [cond_1, cond_2, cond_3]
    
    def create_effects(self) -> List[PddlConditionEffectDto]:

        effect_1 = PddlConditionEffectDto(
            room_patrolled,
            [self._room],
            time=PddlConditionEffectDto.AT_END
        )

        return super().create_effects()
    
def main():
    rclpy.init()
    node = Merlin2RoomPatrolFsmAction()
    node.execute_mission()
    node.join_spin()
    rclpy.shutdown()

if __name__ == "__main__":
    main()