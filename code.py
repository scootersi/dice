import board
import digitalio
import touchio
import adafruit_lis3dh
import busio
import time
import neopixel

touch_A1 = touchio.TouchIn(board.A1)
touch_A2 = touchio.TouchIn(board.A2)
touch_A3 = touchio.TouchIn(board.A3)
touch_A4 = touchio.TouchIn(board.A4)
touch_A5 = touchio.TouchIn(board.A5)
touch_A6 = touchio.TouchIn(board.A6)

i2c = busio.I2C(board.ACCELEROMETER_SCL, board.ACCELEROMETER_SDA)
lis3dh = adafruit_lis3dh.LIS3DH_I2C(i2c, address=0x19)
lis3dh.range = adafruit_lis3dh.RANGE_8_G

pixels = neopixel.NeoPixel(board.NEOPIXEL, 10, brightness=0.2, auto_write=False)

try:
    from audiocore import WaveFile
except ImportError:
    from audioio import WaveFile

try:
    from audioio import AudioOut
except ImportError:
    try:
        from audiopwmio import PWMAudioOut as AudioOut
    except ImportError:
        pass  # not always supported by every board!

# Enable the speaker
spkrenable = digitalio.DigitalInOut(board.SPEAKER_ENABLE)
spkrenable.direction = digitalio.Direction.OUTPUT
spkrenable.value = True

# Make the 2 input buttons
buttonA = digitalio.DigitalInOut(board.BUTTON_A)
buttonA.direction = digitalio.Direction.INPUT
buttonA.pull = digitalio.Pull.DOWN

buttonB = digitalio.DigitalInOut(board.BUTTON_B)
buttonB.direction = digitalio.Direction.INPUT
buttonB.pull = digitalio.Pull.DOWN

def displayNumber(number):

    print("display number: ",number)
    on = (0, 32, 0)
    off = (0, 0, 0)

    for ledIndex in range(9):
        pixels[ledIndex] = off

    for ledIndex in range(9):
        if ledIndex < number:
            pixels[ledIndex] = on
    
    pixels.show()
    
def play_file(number):
    # The two files assigned to buttons A & B
    audiofiles = ["eins.wav", "zwei.wav", "drei.wav", "vier.wav", "funf.wav", "sechs.wav"]

    filename = audiofiles[number]
    print("Playing file: " + filename)
    wave_file = open(filename, "rb")
    with WaveFile(wave_file) as wave:
        with AudioOut(board.SPEAKER) as audio:
            audio.play(wave)
            while audio.playing:
                pass
    print("Finished")

lastState = "unknown"

def motionDetected(x, y, z):
    global lastState
    if (x > -1 and x < 1) and (y > -1 and y < 1) and (z > 9):
        print("Upright")
        if "Upright" != lastState:
            displayNumber(3)
            play_file(2)
        lastState = "Upright"
    if (x > -1 and x < 1) and (y > -1 and y < 1) and (z < -9):
        print("Upside down")
        if "Upside down" != lastState:
            displayNumber(4)
            play_file(3)
        lastState = "Upside down"
    if (x > -1 and x < 1) and (y < -9) and (z > -1 and z < 1):
        print("Charger Up")
        if "Charger Up" != lastState:
            displayNumber(1)
            play_file(0)
        lastState = "Charger Up"
    if (x > -1 and x < 1) and (y > 9) and (z > -1 and z < 1):
        print("Charger Down")
        if "Charger Down" != lastState:
            displayNumber(6)
            play_file(5)
        lastState = "Charger Down"
    if (x > -9) and (y > -1 and y < 1) and (z > -1 and z < 1):
        print("Roll Left")
        if "Roll Left" != lastState:
            displayNumber(2)
            play_file(1)
        lastState = "Roll Left"
    if (x < 9) and (y > -1 and y < 1) and (z > -1 and z < 1):
        print("Roll Right")
        if "Roll Right" != lastState:
            displayNumber(5)
            play_file(4)
        lastState = "Roll Right"

while True:
    if buttonA.value:
        play_file(audiofiles[0])
    if buttonB.value:
        play_file(audiofiles[1])
    if touch_A1.value:
        play_file(audiofiles[0])
    if touch_A2.value:
        play_file(audiofiles[1])
    if touch_A3.value:
        play_file(audiofiles[2])
    if touch_A4.value:
        play_file(audiofiles[3])
    if touch_A5.value:
        play_file(audiofiles[4])
    if touch_A6.value:
        play_file(audiofiles[5])

    x, y, z = lis3dh.acceleration

    event = abs(x) + abs(y) + abs(z)
    #print("event mag: ", event)
    if event > 10:
        motionDetected(x, y, z)
    
    time.sleep(0.1)

