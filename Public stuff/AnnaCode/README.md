# AnnaCode

Two browser pages for building small neural networks and connecting them to
LEGO Education hardware (motors, color sensor, controller). Nothing to
install: Python runs in the page via [PyScript](https://pyscript.net).

| Page | What it does | Open |
|---|---|---|
| **Builder** (`index.html`) | Wire sensors into a network by hand and set the weights yourself. Outputs drive motors, lights and the beeper. | [Open](https://chrisbuerginrogers.github.io/ME193-Robotics/Public%20stuff/AnnaCode/) |
| **Trainer** (`trainer.html`) | The same tool plus a dataset and training: collect examples from your hardware, train the network, and watch the fit and loss plots. | [Open](https://chrisbuerginrogers.github.io/ME193-Robotics/Public%20stuff/AnnaCode/trainer.html) |

| **Table Cloner** (`cloner.html`) | Behavior cloning with a lookup table instead of a network, for a car with a Double Motor and three Color Sensors (left, front, right). See [Table Cloner](#table-cloner-a-car-with-three-color-sensors). | `cloner.html` |

## What you need

- **Chrome or Edge.** Connecting to hardware uses Web Bluetooth, which Safari
  and Firefox don't have. (The trainer still works there with its on-screen
  virtual controller and motor.)
- A LEGO Education hub that is switched on. Turn off other apps connected to
  it first; a hub only talks to one at a time.
- The first load takes a while (the browser downloads Python and numpy).

## Using it

1. Click **Connect device**, pick the hub in the Bluetooth chooser, and click
   **Pair**. The hub beeps when it connects.
2. The device appears in the Devices list, labelled with its card color, for
   example `🟦    Single Motor`. Connect as many as you like.
3. Add inputs, layers and outputs. On each input or output pick a device and a
   channel (for example `Reflection` on a Color Sensor, or `Speed` on a motor).
   The small number beside the device dropdown is that channel's current value.
4. Press the **play** button (▶) to start the network driving the outputs, and the
   stop button (■) to stop it.
5. *Trainer only:* press **Collect** to record rows from the connected inputs and
   outputs into the training data, then **Step** (one epoch) or **Train 50 epochs**.
   **Randomize weights** starts the network over.

Picking a hub that is already connected shows an alert and does nothing.

## Teaching by joystick (Trainer)

Connect a LEGO **Controller** as well as the motor and color sensor, and the
Trainer's **Training data** card gets a *Drive with controller* checkbox. This is
behavior cloning with a human demonstrator, using the controller as the teacher:

1. Set the Output nodes to the motor channels the network should drive (for a
   two-wheeled car: `LeftSpeed` and `RightSpeed`) and the Input node to the
   sensor (for example `Reflection`).
2. Tick **Drive with controller**. The left stick drives the left wheel and the
   right stick drives the right wheel (tank drive); with a single output, whichever
   stick you push harder drives it. **Max speed** caps a full push, and **Reverse**
   flips the direction if forward reads backward.
3. With the neural network *not* running, press **Collect** and drive the robot. Each
   row is the sensor reading and what you *commanded*, not the motor's measured speed,
   so there is no lag in the labels.
4. **Train 50 epochs**, then press **Run**: the network drives.
5. While it runs, **push a stick to take over.** Your command replaces the network's
   and is added to the data as a new row at that sensor reading (the DAgger idea:
   correct the learner where it actually goes). Release and the network resumes.
   Untick *Add my corrections while running* to take over without recording.
   Retrain on the larger dataset and run again.

Light and beep outputs are never driven by the sticks. With the checkbox off,
Collect behaves as before (it records the measured value).

### Reading the Fit plot

The dots are your examples (one color per output). The dark **line** is the network's own
answer for that output, swept across the first input, so training is the line moving onto
the dots. It redraws as you train, as you type a weight, and as you add examples, neurons
or outputs, and it is drawn from the start (the untrained network). If the network has more
than one input, the line varies only the first input and holds the others at their averages
over your examples; a note under the plot says so. The faint dots that appear while the
network runs are what it actually produced ("live"), which should land on the line.

No controller? Add a virtual one (next section). If both a real and a virtual
controller are connected, the first one in the Devices list is used (the status line
under the checkboxes names it).

The joystick-to-motor mapping is `trainer/network/teleop_logic.py` and its tests
run with plain Python from this folder: `python3 -m unittest discover tests -v`.
The wiring is `trainer/misc_ui/teleop.py`. The right wheel is sign-flipped to match
the example networks (opposite signs for the two wheels go straight); if your robot
drives backward, tick **Reverse**.

## Table Cloner: a car with three color sensors

`cloner.html` teaches a car by driving it, and stores what it learns as a table you can read.
Mount the three Color Sensors pointing left, front and right on a Double Motor base.

1. **Connect device** once per hub: the three Color Sensors, the Double Motor and a Controller.
   The sensors fill the Left, Front and Right slots in the order you connect them; swap them
   with the dropdowns if needed.
2. Set what counts as an object: a close object usually *reads brighter* (reflection above
   the threshold). Watch the three live readings light up and adjust the number.
3. Press **Record** and drive with the sticks (left stick = left wheel, right stick = right
   wheel). Ten times a second, the page notes which sensors see an object (8 patterns) and
   whether you went Forward, Left, Right or Back, and adds a tally to that row. Standing
   still teaches nothing.
4. Press **Run table**. Each tick the car looks up its pattern and does the most-tallied action.
   A pattern you never taught borrows the answer from the most similar one you did.
5. **Push a stick to take over.** With *Add my corrections while running* on, your action is
   tallied too, so the table improves where the car actually goes wrong (the DAgger idea).

**Step mode** (experimental, off by default) changes what the joystick does. Instead of driving the wheels
continuously, one push gives one whole move. The **left stick** is forward/back: push it forward to drive
one car length, pull it back to drive one car length backwards. The **right stick** is turn: push it forward
for a 90 degree right turn, pull it back for a 90 degree left turn. Push a stick past about 60%, hold it for
a fifth of a second, and the move starts; bring the sticks back to centre before the next one (if both are
pushed, the one pushed further wins). While recording, each
push is one tally in the table. **Run table** then makes one move at a time: it looks up the pattern, makes
the move, waits for the wheels to stop, and looks again. Pushing a stick between moves takes over, as before.
- **One car length** is a setting in wheel degrees (the Double Motor has no idea how long your car is).
  Start at 360, push forward once, and adjust the number until one push moves one car length.
- Moves use the Double Motor's own `movement_move_for_degrees` and `movement_turn_for_degrees`; the turn
  is confirmed by the hub's rotation sensor. The page decides a move is finished when the wheel speeds
  have stayed at zero for a third of a second (or after 8 seconds).
- **Driving speed** is the speed of each move. **Reverse** swaps forward and back (not the turns).
- Logic: `classify_step`, `StepTrigger`, `MoveClock` and `step_plan` in `cloner/table_logic.py` (tested); wiring in
  `cloner/main.py`. Not yet tried on a real car.

**Save power** (off by default here) keeps the three Color Sensors' lights off while the page is
idle. They come on when you press Record or Run (the page waits until they are really reading
before it starts) and go off again when you stop. It is the same Save power as the Trainer's: the
sensor's mode is set with the library's `set_color_sensor_mode`, and the code is shared
(`trainer/misc_ui/power.py`, `trainer/network/power_logic.py`). It is off by default because
the live readings go blank while a light is off, and you need them to set the threshold. Tick
it once the threshold is right.

The table is saved in the browser. **Clear table** starts over. Hub, Bluetooth and joystick code is
shared with the Trainer (`trainer/Device.py`, `trainer/network/teleop_logic.py`); the table logic is
`cloner/table_logic.py` (pure Python, tested in `tests/test_table_logic.py`) and the page wiring is
`cloner/main.py`. There are no virtual devices on this page, so it needs the real hardware and Chrome or Edge.

## No kit with you? Virtual devices (Trainer)

In the Devices card, pick a device from **Choose a virtual device…** and press **Add**.
A card for it appears (with a short "Added ..." confirmation next to the button) and it
shows up in every Input and Output dropdown. It behaves like the real one. Use as many
as you like, mixed with real hardware or on their own (no Bluetooth needed, so it also
works in Safari and Firefox). The **×** on a card removes it.

| Virtual device | Channels it shows | Notes |
|---|---|---|
| Controller | `LeftPercent`, `RightPercent` | Two sliders, plus the keyboard (below) |
| Double Motor | `LeftSpeed`, `RightSpeed`, `BothSpeed`, `LeftPosition`, `RightPosition`, `LeftAngle`, `RightAngle`, `LeftPower`, `RightPower` | Wheels are mirrored like the real chassis. Outputs: `LeftSpeed`, `RightSpeed`, `BothSpeed` |
| Single Motor | `Speed`, `Position`, `Angle`, `Power` | Output: `Speed` |
| Color Sensor | `Reflection` | Slide it to change what the sensor "sees" (0 dark, 100 bright) |

**Keyboard for the virtual controller** (works whenever you are not typing in a box;
Cmd/Ctrl shortcuts are left alone):

- **Arrow keys** drive like a car: up/down = both sticks forward/back, left/right = turn.
- **W / S** = left stick up/down, **I / K** = right stick up/down.
- The sticks ease out while a key is held and spring back when you let go.

With a virtual controller you can do the whole loop at home: add a controller, a color
sensor and a motor, tick **Drive with controller**, **Collect** while you slide the
sensor and drive with the keys, train, and **Run**.

Virtual devices only have the channels listed above (a real device reports more, such
as the IMU and color channels). Their logic is `trainer/misc_ui/virtual_devices.py`,
with the numbers in `trainer/network/virtual_logic.py` (unit-tested).
`trainer.html?virtual` still works and shows the older single combined controller
and motor panel.

## Saving the color sensor's battery (Trainer)

The color sensor's light is a real battery drain (one sensor went 80% to 30% to dead in a
single session), and it used to stay on for as long as the sensor was connected. The
**Save power** box in the Devices card (ticked by default) keeps a connected Color Sensor
**off** except while you are **Collect**ing or the network is **Run**ning, and only if an
Input node reads that sensor. The sensor's chip says "light off" while it is off.

- Pressing **Collect** or **Run** turns the light on and waits (up to 2 seconds) until the
  sensor is really reading before the first row is recorded or the first motor command goes
  out, so you never train or drive on a stale reading. **Stop** turns it off again.
- **The cost:** with the light off, the sensor's live reading is blank. To watch the sensor
  live (to see what it reads over the tape, say), untick **Save power**; the light comes
  straight back on.
- A sensor that Save power switched off is allowed to be quiet; the chip won't call it
  "No signal". A sensor that should be on and goes silent is still flagged.

How it works, and what is not verified: the page asks the sensor for a mode with the library's
own `set_color_sensor_mode` (without waiting for the reply) and reads the mode the sensor says it is
in from every color reading. This was checked against fake sensors only. With a real sensor,
look in the browser console (Cmd+Opt+J) for `asked the sensor for mode 0 (light off)` and
watch the light go dark. If a sensor never obeys, the page asks four times, says so once in
the console, and leaves it alone; untick **Save power** to stop it asking. The logic is in
`trainer/network/power_logic.py` (unit-tested) and `trainer/misc_ui/power.py`.

## Troubleshooting

- **A device chip turns red and says "Disconnected" or "No signal" (Trainer).**
  *Disconnected* means the browser reported that the Bluetooth link dropped, for example
  the laptop went to sleep, the device ran out of power, or it moved out of range. While
  a device is disconnected the page stops sending it commands, ignores a disconnected
  controller's sticks (they would otherwise stay stuck at their last value), and stops
  **Run** or **Collect** if an input or output in use has dropped. *No signal* means the
  page has heard nothing for several seconds but the browser has not reported a drop. It is
  only a warning and clears by itself if data returns. To recover from a disconnect, click
  the chip's **x** and press **Connect device** again.
- **Battery percentage.** Each device only reports its battery level when it chooses to, and
  the page can only show what it is sent. Hover over a chip's battery to see when the last
  report arrived and how many reports there have been. The browser console (Cmd+Opt+J)
  logs a `battery reading` line for every report. A battery number on a red chip may be
  out of date.
- **It connects only some of the time.** The page retries automatically
  (up to five attempts). Open the browser console (Cmd+Opt+J) to see
  `BLE connect attempt N/5 failed` lines.
- **A hub appears in the chooser with no name.** Chrome sometimes does not
  report the name. The page works out the device type from the data the hub
  sends, and falls back to asking you which type it is.
- **Nothing happens on load.** Hard-reload (Cmd+Shift+R). The page needs the
  internet to fetch PyScript and Plotly.
- **Hub won't connect at all.** Switch it off and on, and remove any stale
  entry for it in your computer's Bluetooth settings.

## For editing

Everything is plain files; there is no build step. To run a copy locally:

```
cd "Public stuff/AnnaCode"
python3 serve.py
```

then open `http://localhost:8000/AnnaCode/` (builder) or
`http://localhost:8000/AnnaCode/trainer.html` (trainer) in Chrome. `localhost` is
allowed to use Bluetooth. `python3 serve.py 8001` picks another port. The server
serves the whole `Public stuff` folder, because both pages load the shared
`../QLearn/webhub.py`.

`serve.py` is `python3 -m http.server` with browser caching switched off. Prefer it when
you edit files or switch branches: the plain server lets Chrome keep old copies, and
PyScript fetches its `.py` files itself, so the page can keep running stale code (for
example a new button that does nothing) even after a hard reload.

```
index.html, styles.css, main.py   Builder page and its entry point
Device.py                         Hub connection, device state, output routing
glue/ network/ misc_ui/ plot.py   Builder UI, network model, plotting
JS/ble.js                         Web Bluetooth wrapper (connect with retries)
pyscript.toml                     Builder config: packages and file map
trainer.html, trainer.toml        Trainer page and its config
trainer/                          Trainer sources (same layout, own copies)
```

Notes:

- **Flat Python imports.** PyScript copies each source file into one flat
  folder (`./glue/state.py` becomes `state.py`), so modules import each other
  as `import state`, not `from glue import state`. The mapping lives in the
  `[files]` table of `pyscript.toml` / `trainer.toml`. Add a new file there
  or it won't be found.
- **The two pages have separate copies of `Device.py`.** A fix to Bluetooth
  handling must be made in both `Device.py` and `trainer/Device.py`
  (`JS/ble.js` and `trainer/JS/ble.js` likewise).
- **`legoeducation` is pinned to 1.2.0** in `trainer.toml` and `cloner.toml` (the Builder's
  `pyscript.toml` is still on 1.0.6 and its own copy of `Device.py`), so those pages understand
  the latest hub firmware. Bluetooth still goes through `ble.js`: `webhub.py` (shared with
  QLearn, loaded from `../QLearn/webhub.py`) registers a transport for the library's sending,
  and checks each hub's firmware when it connects. A hub with older firmware gets an alert to
  update at code.legoeducation.com and is disconnected. Keep the pin at 1.2.0 or later: earlier
  versions cannot read current firmware.
- The builder page still includes the original PyScript analytics snippet;
  the trainer page does not.

## Where it came from

Adapted from the Tufts CEEO apps
[network-builder](https://tuftsceeo.pyscriptapps.com/network-builder/latest/)
and [network-trainer](https://tuftsceeo.pyscriptapps.com/network-trainer/latest/)
(source: [tuftsceeo/NeuralNetworkEducation](https://github.com/tuftsceeo/NeuralNetworkEducation)).
Changes here: more reliable Bluetooth pairing, hub type detection when Chrome
gives no name, card-color labels, an already-connected alert, live values next
to each device dropdown, and a trainer page without the lesson plans.
