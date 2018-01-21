#define BTN_KEY 9
#define BTN_TALK 10

int incomingByte = 0;

void high(int pin) {
    digitalWrite(pin, HIGH);
}

void low(int pin) {
    digitalWrite(pin, LOW);
}

void cleanup() {
    low(BTN_KEY);
    low(BTN_TALK);
}

void pressKey() {
    cleanup();
    delay(250);
    high(BTN_KEY);
    delay(500);
    cleanup();
}

void pressTalk() {
    cleanup();
    delay(250);
    high(BTN_TALK);
    delay(500);
    cleanup();
}

void openDoor() {
     pressKey();
     pressTalk();
     pressKey();
     delay(5000);
     pressTalk();
}

void testDoor() {
     pressKey();
     delay(2000);
     pressKey();
}

void setup()
{
    pinMode(BTN_TALK, OUTPUT);
    pinMode(BTN_KEY, OUTPUT);
    cleanup();
    Serial.begin(9600);
}

void loop()
{
    if (Serial.available() > 0) {
        incomingByte = Serial.read();
        if (incomingByte == 1) {
            openDoor();
	}
	if (incomingByte == 2) {
	   testDoor();
	}
    }
}
