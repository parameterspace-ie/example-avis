# Resource AVI

This is an AVI closely based on the Simple AVI example.

It includes a RAM resource slider. This is used to populate the 'resources_ram_mb' attribute of the AviJob model. 
This attribute has no bearing on the AVI when it's developed in STANDALONE mode.

But when it is deployed within the GAVIP portal, it is used to configure how much RAM a pipeline is allocated.

This example shows how a user may be able to allocate the RAM freely.
Alternatively, the AVI could determine the RAM without exposing the choice to the user.
Or, the AVI could provide a recommendation.

