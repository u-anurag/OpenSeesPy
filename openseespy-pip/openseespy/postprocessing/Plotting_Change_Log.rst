A list of changes in plotting commands for version 3 release.


``saveFiberData2D()``:

A new optional argument ``ZLE=False`` was added. By default, the command records fiber data for a non-linear section. With ``ZLE=True``, it changes the recorder to save fiber data for a zero-length element.
ZLE is a boolean. It’s used to specify if the section is part of a zero length element or not.


``plot_deformedshape()``:

This function has two new kwargs: monitorEleTags, monitorOutFile. ``monitorEleTags`` is a list of elements to be plotted in the deformed shape. It is useful in focusing on a specific part in big structures.
``monitorOutFile`` is a placeholder argument. The purpose is to enable users in highlight the elements if a specific output quantity (ex. deformation, stress, strain, rotation) has exceeded its limit assigned by the user.


