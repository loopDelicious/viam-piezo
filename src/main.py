import asyncio
from typing import Any, ClassVar, Final, Mapping, Optional, Sequence, cast

from typing_extensions import Self
from viam.components.generic import *
from viam.module.module import Module
from viam.proto.app.robot import ComponentConfig
from viam.proto.common import ResourceName
from viam.resource.base import ResourceBase
from viam.resource.easy_resource import EasyResource
from viam.resource.types import Model, ModelFamily
from viam.utils import struct_to_dict
from viam.components.board import Board


class Piezo(Generic, EasyResource):
    MODEL: ClassVar[Model] = Model(ModelFamily("joyce", "buzzer"), "piezo")

    @classmethod
    def new(
        cls, config: ComponentConfig, dependencies: Mapping[ResourceName, ResourceBase]
    ) -> Self:
        """This method creates a new instance of this Piezo component.
        """
        return super().new(config, dependencies)

    @classmethod
    def validate_config(cls, config: ComponentConfig) -> Sequence[str]:
        """This method allows you to validate the configuration object received from the machine,
        as well as to return any implicit dependencies based on that `config`.
        """
        fields = config.attributes.fields

        if "piezo_pin" in fields:
            if not fields["piezo_pin"].HasField("string_value") or not fields["piezo_pin"].string_value.isdigit():
                raise Exception("Piezo pin must be configured as a numeric string (digits only).")

        if "board" in fields:
            if not fields["board"].HasField("string_value"):
                raise Exception("Board name must be configured as a string.")

        return []

    def reconfigure(
        self, config: ComponentConfig, dependencies: Mapping[ResourceName, ResourceBase]
    ):
        """This method allows you to dynamically update your service when it receives a new `config` object.
        """
        attrs = struct_to_dict(config.attributes)

        self.pin = attrs.get("piezo_pin")
        self.logger.debug("Using pin: " + str(self.pin))

        self.board = attrs.get("board")
        self.logger.debug("Using board: " + str(self.board))
        boardResourceName = Board.get_resource_name(self.board)
        self.board = dependencies.get(boardResourceName)
        if not isinstance(self.board, Board):
            raise Exception(f"Board '{boardResourceName}' not found during reconfiguration.")

        return super().reconfigure(config, dependencies)
    
    async def sound_buzzer(
        self,
        frequency: int = 1000,
        duration: float = 1.0,
        duty_cycle: float = 0.5,
        *,
        timeout: Optional[float] = None,
        **kwargs
    ) -> str:
        """Activate the buzzer with the specified parameters."""
        try:
            if not isinstance(frequency, (int, float)) or frequency <= 0:
                raise ValueError(f"Frequency must be a positive number. Got: {frequency}")
            if not isinstance(duration, (int, float)) or duration <= 0:
                raise ValueError(f"Duration must be a positive number. Got: {duration}")
            if not isinstance(duty_cycle, (float, int)) or not 0 <= duty_cycle <= 1:
                raise ValueError(f"Duty cycle must be between 0 and 1. Got: {duty_cycle}")
            
            frequency = int(frequency)

            self.logger.info(f"Activating buzzer: frequency={frequency}, duration={duration}, duty_cycle={duty_cycle}")
            self.logger.info(f"Board object: {self.board}")
            self.logger.debug(f"Pin name: {self.pin} (type: {type(self.pin)})")

            gpio_pin = await self.board.gpio_pin_by_name(name=self.pin)
            self.logger.debug(f"Retrieved GPIO pin: {gpio_pin}")

            await gpio_pin.set_pwm_frequency(frequency)
            await gpio_pin.set_pwm(duty_cycle) 
            await asyncio.sleep(duration)
            await gpio_pin.set_pwm(0.0) 

            self.logger.info("Buzzer operation completed successfully.")
            return "Buzzer sounded successfully."

        except Exception as e:
            self.logger.error(f"Error in sound_buzzer: {e}")
            return f"Error in sound_buzzer: {e}"
        
    async def do_command(
        self,
        command: dict[str, Any],
        *,
        timeout: Optional[float] = None,
        **kwargs
    ) -> dict[str, Any]:
        """Handle runtime commands for the Piezo component."""
        result = {}

        for name, args in command.items():
            if name == "sound_buzzer":
                try:
                    frequency = args.get("frequency", 1000)  # Default frequency: 1000 Hz
                    duration = args.get("duration", 1.0)    # Default duration: 1 second
                    duty_cycle = args.get("duty_cycle", 0.5)  # Default duty cycle: 50%

                    await self.sound_buzzer(frequency=frequency, duration=duration, duty_cycle=duty_cycle)
                    result["sound_buzzer"] = f"Buzzer activated: {frequency}Hz for {duration}s with {duty_cycle*100}% duty cycle."
                except Exception as e:
                    self.logger.error(f"Error in do_command (sound_buzzer): {e}")
                    result["sound_buzzer"] = f"Error: {str(e)}"

            elif name == "play_harry_potter":
                try:
                    await self.play_harry_potter()
                    result["play_harry_potter"] = "Played Harry Potter theme song."
                except Exception as e:
                    self.logger.error(f"Error in do_command (play_harry_potter): {e}")
                    result["play_harry_potter"] = f"Error: {str(e)}"

            else:
                result[name] = f"Unknown command: {name}"


        return result

    async def play_harry_potter(self):
        """Play Harry Potter's Hedgwig's theme song using the piezo buzzer."""
        # Define the melody (frequency in Hz) and rhythm (duration in seconds)
        melody = [
            622, 740, 784, 740, 622, 784, 740, 622, 740, 784, 622, 740, 622, 587, 622, 659,
            740, 622, 740, 784, 622, 587
        ]
        rhythm = [
            0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.8, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.8,
            0.4, 0.4, 0.4, 0.4, 0.4, 0.8
        ]

        try:
            self.logger.info("Playing Harry Potter theme song.")
            
            # Get the GPIO pin
            gpio_pin = await self.board.gpio_pin_by_name(name=self.pin)
            
            for frequency, duration in zip(melody, rhythm):
                self.logger.debug(f"Playing note: frequency={frequency}, duration={duration}")
                
                # Play the note
                await gpio_pin.set_pwm_frequency(int(frequency))
                await gpio_pin.set_pwm(0.5)  # 50% duty cycle
                await asyncio.sleep(duration)
                
                # Pause between notes
                await gpio_pin.set_pwm(0.0)
                await asyncio.sleep(0.1)
            
            self.logger.info("Finished playing Hedwig's Theme.")
        except Exception as e:
            self.logger.error(f"Error in play_harry_potter: {e}")


if __name__ == "__main__":
    asyncio.run(Module.run_from_registry())