#!/bin/sh
rm submission.zip

zip -r submission ./hlt

cp uncoolshogun_0.0.1.py MyBot.py

zip submission MyBot.py

rm MyBot.py
