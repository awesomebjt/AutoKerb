import math
import time
import krpc
import AutoKerb

turn_start_altitude = 250
turn_end_altitude = 45000
target_altitude = 85000

conn = krpc.connect(name='Launch into orbit')
vessel = conn.space_center.active_vessel
# Pre-launch setup
vessel.control.sas = False
vessel.control.rcs = False
vessel.control.throttle = 0.8

vessel.control.activate_next_stage()
vessel.auto_pilot.engage()

gt = AutoKerb.GravityTurn(conn, turn_start_altitude, turn_end_altitude, target_altitude)
st = AutoKerb.AutoStaging(krpc_connection=conn)
gt.start()
st.start()