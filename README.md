# Python device simulator [Still on progres...]

I created this to simulate simple devices that will communicate to EPICS IOCs in order to test an EPICS Kubernetes environment.

# Basic protocol

Each device has a list of parameters that can be read.
If the protocol is well coded, it should work like:

```
# Requisition for reading
Client: R:paramName:
Device: S:paraName:Value

# Error codes and such
Client: Something_That_does_not_go_well
Device: E:Error_Message:

# Requisition for writing
Client: W:paraName:newValue
Device: S:paraName:newValue
```

# Installation and Usage

This is not on PYPI so to install:

```
pip3 install git+https://github.com/marcomontevechi1/device-simulator
```

To create devices:
```
device-pool -n <Number>
```

This will create Number devices and you will se something like:

```
DeviceSim0: Added name DeviceSim0 to devices list.
DeviceSim1: Added name DeviceSim1 to devices list.
DeviceSim0: Bound socket to 0.0.0.0:34055
DeviceSim2: Added name DeviceSim2 to devices list.
DeviceSim1: Bound socket to 0.0.0.0:42411
DeviceSim2: Bound socket to 0.0.0.0:44239
(...)
```

I didn't extensively test the source file functionality, but it also should work:

```
device-pool -s <Yaml file>
```

On another terminal:
```
telnet localhost <PORT>
```

If there is a device on localhost:PORT it will connect and answer to the protocol.


