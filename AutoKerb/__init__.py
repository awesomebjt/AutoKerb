import krpc
from threading import Thread


class AutoStaging(Thread):
    def __init__(self, krpc_connection, final_stage_index=2):
        Thread.__init__(self)
        self.krpc_connection = krpc_connection
        self.final_stage = final_stage_index

    def run(self):
        print("Starting AutoStaging thread...")
        # TODO: Execute staging whenever fuel runs out and there is at least one more stage left with fuel in it.
        vessel = self.krpc_connection.space_center.active_vessel
        while True:
            engines = vessel.parts.engines
            max_decouple_stage = max([e.part.decouple_stage for e in engines])
            empty = max([x.amount for x in vessel.resources_in_decouple_stage(max_decouple_stage, cumulative=False).all]) == 0.0
            if vessel.situation.name == 'flying' and empty:
                print("Empty decouple stage detected, staging...")
                vessel.control.activate_next_stage()


class GravityTurn(Thread):
    def __init__(self, krpc_connection, start_altitude, end_altitude, target_apoapsis):
        Thread.__init__(self)
        self.krpc_connection = krpc_connection
        self.start_altitude = start_altitude
        self.end_altitude = end_altitude
        self.target_apoapsis = target_apoapsis
    def run(self):
        print("Starting Gravity Turn thread...")
        conn = self.krpc_connection
        vessel = conn.space_center.active_vessel

        ut = conn.add_stream(getattr, conn.space_center, 'ut')
        altitude = conn.add_stream(getattr, vessel.flight(), 'mean_altitude')
        apoapsis = conn.add_stream(getattr, vessel.orbit, 'apoapsis_altitude')

        vessel.auto_pilot.target_pitch_and_heading(90, 90)
        turn_angle = 0
        while True:
            # Do the Gravity turn
            if self.start_altitude < altitude() < self.end_altitude:
                frac = ((altitude() - self.start_altitude) /
                        (self.end_altitude - self.start_altitude))
                new_turn_angle = frac * 90
                if abs(new_turn_angle - turn_angle) > 0.5:
                    turn_angle = new_turn_angle
                    vessel.auto_pilot.target_pitch_and_heading(90 - turn_angle, 90)
            if apoapsis() > self.target_apoapsis * 0.9:
                print('Approaching target apoapsis')
                break
        vessel.control.throttle = 0.2
        while apoapsis() < self.target_apoapsis:
            pass
        print('Target apoapsis reached')
        vessel.control.throttle = 0.0


class MaintainHeading(Thread):
    def run(self, heading):
        # TODO: Stay aimed at a particular heading regardless of pitch
        pass

