import time

import schedule

import displayRun

#Do not use when using witty pi (to use and schedule in a chron job)
def main():
    schedule.every().day.at("00:00").do(displayRun.main)
    schedule.every(12).hours.do(displayRun.main)

    displayRun.main()
    while True:
        schedule.run_pending()
        time.sleep(5)


if __name__ == '__main__':
    main()
