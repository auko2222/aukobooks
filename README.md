# aukobooks
Completes ALL assignments in zybooks, **regardless if it's a participation or challenge activity.**





## FAQ

#### How do I use the program?

Clone the repo to desktop, extract the zip, and then run **"aukobook.bat"**.

Once you're in the menu, **login with your Zybook Credentials**.

#### Are my credentials safe?

**Yes**, nothing is saved. Everything is handled on your machine/browser.

#### Can ZyBook/Teachers catch me using this?

**No**, if you use "legit mode" which adds realistic delays to completing assignments. You can run it in the background while it does all of the hard labor for you. On top of this, the network requests sent to ZyBooks use the exact requests if the assignment were to be done legitimately.

#### I'm super interested in how this works! How does it work?

Your Zybooks **Token** (your current session) is used to put together a **checksum** in order to send a valid request to Zybooks.

A **checksum** is like a password that's calculated for each activity in your chapter and is used to build a request that looks like:


```python
{
    "part": 0,
    "complete": 1, # tells zyboks the current activity is complete
    "timestamp": ...
    "checksum": md5(path + timestamp + token + id + part + complete + buildkey)
}
```

ZyBooks receives the checksum, and if valid, marks the activity as complete and moves to the next one.

#### Can this be patched?

**Probably**, and if it does, I'm not maintaining it. Feel free to check out the code for yourself.


## Screenshots

![App Screenshot](https://media.discordapp.net/attachments/1263769407801262100/1468156169951510687/image.png?ex=6982fe7b&is=6981acfb&hm=8fdf637a343ea0c44333a4f7a470c652c4a35493520d29106b8c1adca4ce6cb9&=&format=webp&quality=lossless)

![App Screenshot](https://cdn.discordapp.com/attachments/1263769407801262100/1468172653855641600/image.png?ex=69830dd6&is=6981bc56&hm=9bedaeaf8087756b683cae67245e137ff84ab9883df0d6f9ffc72e9472bd1986&)
