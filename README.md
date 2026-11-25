# CSCI2730 Project: A Simple Backend Blockchain System with Falcons Encrpytion

**Installation**

Python version: 3.10.12
Required Package: Flask, qcrypto

```
pip install Flask
pip install qcrypto
```

**How To Use**

1. Start the Bootnode first. The default port number is 9000.

```
python3 -m network.bootnode
```

2. Start the Client with:

   1. port
   2. bootnode address with port (127.0.0.1:9000)
   3. wallet file (json file), For first time, can be a non-exist file
   4. balance (only for the init system purpose

   ```
   python3 -m client --port 8000 --bootnode 127.0.0.1:9000 --wallet wallet1.json --balance 100
   ```

**REMINDER**

1. The system does not implement the initial money. So, it is better to use one Client as the money initiator.
2. Although the system implement POW, but miner will not be rewarded. Therefore, the money in the system always keep constant until a Client entering with new balance
