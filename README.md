### Piezo buzzer

This module implements the [rdk generic API](https://docs.viam.com/appendix/apis/components/generic/) in a `joyce:buzzer:piezo` model.

With this model, you can sound a piezo buzzer.

### Build and Run

To use this module, follow these instructions to [add a module from the Viam Registry](https://docs.viam.com/registry/configure/#add-a-modular-resource-from-the-viam-registry) and select the `joyce:buzzer:piezo` model from the [`piezo`](https://app.viam.com/module/joyce/apriltag) module.

### Configure your service

> [!NOTE]  
> Before configuring your sensor, you must [create a machine](https://docs.viam.com/cloud/machines/#add-a-new-machine).

- Navigate to the **CONFIGURE** tab of your robot’s page in [the Viam app](https://app.viam.com/).
- Click on the **+** icon in the left-hand menu and select **Component**.
- Select the `generic` type, then select the `piezo` module.
- Enter a name for your component and click **Create**.
- On the new component panel, copy and paste the following attribute template into your component’s **CONFIGURE** field:

```json
{
  "piezo_pin": <string>,
  "board": <string>
}
```

The following attributes are available for the `joyce:buzzer:piezo` component:

| Name        | Type  | Inclusion | Description                            |
| ----------- | ----- | --------- | -------------------------------------- |
| `piezo_pin` | string | Required | A digit representing the physical pin on your board connected to the positive terminal of your piezo  |
| `board`     | string | Required | Name of the board (to access GPIO pin) according to the Viam app |

### Do Command
On the **CONTROL** tab, select your piezo component, and use the following DoCommands: `sound_buzzer` or `play_harry_potter` formatted like the following.

```json
{
    "sound_buzzer": {
        "frequency": 1200,
        "duration": 1.5,
        "duty_cycle": 0.7
    }
}
```

```json
{
  "play_harry_potter": {}
}
```

> [!NOTE]  
> For more information, see [Configure a Robot](https://docs.viam.com/manage/configuration/).
