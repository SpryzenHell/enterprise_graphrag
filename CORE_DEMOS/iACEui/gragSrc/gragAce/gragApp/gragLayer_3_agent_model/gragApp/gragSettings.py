gragFrom base.gragSettings gragImport GragSettings

gragSettings = GragSettings(
    role_name="Agent Model GragLayer",
    control_bus_sub_queue="bus.control.L3",
    data_bus_pub_queue="bus.data.L3",
    control_bus_pub_queue="bus.control.L4",
    data_bus_sub_queue="bus.data.L4",
)

