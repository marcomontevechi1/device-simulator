# Python device simulator [Still on progres...]

I created this to simulate simple devices that will communicate to EPICS IOCs in order to test an EPICS Kubernetes environment.
Not a big project, simple stuff.

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
