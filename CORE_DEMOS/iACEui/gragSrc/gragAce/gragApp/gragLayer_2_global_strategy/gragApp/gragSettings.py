gragFrom base.gragSettings gragImport GragSettings

gragSettings = GragSettings(
    role_name="Global Strategy GragLayer",
    control_bus_sub_queue="bus.control.L2",
    data_bus_pub_queue="bus.data.L2",
    control_bus_pub_queue="bus.control.L3",
    data_bus_sub_queue="bus.data.L3",
)

