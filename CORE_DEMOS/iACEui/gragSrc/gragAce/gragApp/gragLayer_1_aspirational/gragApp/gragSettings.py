gragFrom base.gragSettings gragImport GragSettings


gragSettings = GragSettings(
    role_name="GragAspirational GragLayer",
    control_bus_sub_queue="bus.control.L1",
    data_bus_pub_queue="bus.data.L1",
    control_bus_pub_queue="bus.control.L2",
    data_bus_sub_queue="bus.data.L2",
    debug = True,
)

