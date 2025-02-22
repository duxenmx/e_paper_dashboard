"""Supporting functions for the E_ink_dashboard project."""

import time
import datetime
import calendar
import random
import os
import requests
from PIL import Image, ImageDraw, ImageFont
from waveshare_epd import epd7in5_V2

picdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'pic')
fontdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'font')

epd = epd7in5_V2.EPD()

# Set the colors
black = 'rgb(0,0,0)'
white = 'rgb(255,255,255)'


def url_content(base_url, module_name, header_dict, error_color):
    """Retrieve the content at base_url.  If connection fails or the status code is anything but 200, display an error."""

    response_content = None
    error_connect = True
    while error_connect is True:
        try:
            # HTTP request
            # print(module_name + ': Attempting to connect to API: ' + base_url)
            if header_dict:
                response_content = requests.get(str(base_url), headers=header_dict)
            else:
                response_content = requests.get(str(base_url))
            # print('Connection to API successful.')
            error_connect = None
        except:
            # Call function to display connection error
            print(module_name + ': Connection error.')
            # error_connect = None
            display_error(module_name + ' API connection failed', error_color)
            # break
    # Check status of code request
    if response_content.status_code != 200:
        display_error(module_name + ': Return code not 200, was ' +
                      str(response_content.status_code), error_color)
        # Should we force content to null if the response code is not 200?
        # response_content = None

    return response_content


def choose_mod(mod_choice, mod_turn):
    """Unknown."""

    if mod_choice in ("weather", "transit", "tasklist"):
        mod_turn = 0
    elif mod_choice in ("c-s", "news", "meetings"):
        mod_turn = 1
    elif mod_choice in ("spotify"):
        mod_turn = 2
    elif mod_choice == "off":
        mod_turn = 3
    elif mod_choice == "random":
        mod_rand = random.randint(0, 1)
        while mod_rand == mod_turn:
            mod_rand = random.randint(0, 1)
        if mod_turn != mod_rand:
            mod_turn = mod_rand
    else:
        print("mode unknown,  going to default  mode")
        mod_turn = 0
    return mod_turn


def time_in_range(start_hour, end_hour):
    """Return true if x is in the range [start, end]"""

    start = datetime.time((start_hour), 0, 0)
    end = datetime.time((end_hour), 0, 0)
    current_hour = datetime.datetime.now().strftime('%H')
    current_min = datetime.datetime.now().strftime('%M')
    current_sec = datetime.datetime.now().strftime('%S')
    x = datetime.time(int(current_hour), int(current_min), int(current_sec))
    if start <= end:
        return start <= x <= end
    else:
        return start <= x or x <= end


def tir_min(hour, x_min, y_min, y_sec):
    """Return true if x is in the range [start, end]"""

    start = datetime.time((hour),  (x_min), 0)
    end = datetime.time((hour),  (y_min), (y_sec))
    current_hour = datetime.datetime.now().strftime('%H')
    current_min = datetime.datetime.now().strftime('%M')
    current_sec = datetime.datetime.now().strftime('%S')
    x = datetime.time(int(current_hour), int(current_min), int(current_sec))
    if start <= end:
        return start <= x <= end
    else:
        return start <= x or x <= end


def sep_strings(it_str, chk_start):
    """Appears to split string at the last space before or at a maximum string length."""

    chk_str = int(len(str(it_str)))
    chk_str_1 = chk_str
    check = False
    # print("before" + str(chk_str))
    if chk_str > chk_start:
        chk_str = chk_start
    else:
        # chk_str = chk_str		#Does no action, not needed.
        check = True
    # print("after" + str(chk_str))
    while check is False:
        if str(it_str)[chk_str] != " ":
            chk_str = chk_str - 1
            # print("space_false: " + str(chk_str))
            check = False
        else:
            # chk_str = chk_str		#Does no action, not needed.
            # print("space_true: " + str(chk_str))
            check = True

    if chk_str_1 >= chk_start:
        sep_it_1 = str(it_str)[0: chk_str] + " "
        sep_it_2 = str(it_str)[chk_str+1: chk_str_1] + " "

    else:
        sep_it_1 = str(it_str)[0: chk_str] + " "
        sep_it_2 = " "

    return sep_it_1, sep_it_2


def draw_cal_mod(cal_s_x_0, cal_s_y, draw, color_1, color_2):
    """Draw the calendar for this month."""

    cal_month = datetime.datetime.now().month
    cal_year = datetime.datetime.now().year
    cal_day = datetime.datetime.now().day
    cal_n_m = calendar.month_name[cal_month]
    cal_text = calendar.TextCalendar(calendar.MONDAY)
    cal_list = cal_text.monthdayscalendar(cal_year, cal_month)
    cal_s_x = cal_s_x_0

    draw.text((cal_s_x + 60, cal_s_y-65), str(cal_n_m) + ' ' + str(cal_year),
              font=font_size(35), fill=color_1)
    draw.text((cal_s_x, cal_s_y-25), 'MO     TU     WED    THU    FRI    SAT     SU',
              font=font_size(22), fill=color_1)

    for cal_x in range(len(cal_list)):
        for cal_y in (0, 1, 2, 3, 4, 5, 6):
            if cal_list[cal_x][cal_y] != 0:

                if cal_list[cal_x][cal_y] == cal_day:
                    draw.rectangle((cal_s_x-5, cal_s_y, cal_s_x+22, cal_s_y+28), fill=color_1)
                    draw.text((cal_s_x, cal_s_y), str(
                        cal_list[cal_x][cal_y]), font=font_size(22), fill=color_2, align='right')
                else:
                    draw.text((cal_s_x, cal_s_y), str(
                        cal_list[cal_x][cal_y]), font=font_size(22), fill=color_1, align='right')
            cal_s_x = cal_s_x + 55
        cal_s_x = cal_s_x_0
        cal_s_y = cal_s_y + 30


def font_size(size):
    """Return a BAHNSCHRIFT font at the requested size."""
    return ImageFont.truetype(os.path.join(fontdir, 'BAHNSCHRIFT.TTF'), size)


def get_time(local_time):
    """Return Weekday, Month name and day of the month of the given time."""

    pst_time = time.localtime(int(local_time))
    pst_time = time.strftime('%A, %b %d', pst_time)
    return pst_time


def get_year():
    """Unsure - function name implies this returns a year, but it returns yyyy-mm-dd."""

    datetime_object = datetime.datetime.now()
    year_str = (str(datetime_object.year) + "-" +
                str(datetime_object.month) + "-" + str(datetime_object.day))
    return year_str


def dayname():
    """Return today's name."""
    return datetime.datetime.now().strftime("%A")


def cur_hr():
    """Return 24 hour (0 padded) current hour."""
    return datetime.datetime.now().strftime("%H")


def isTimeFormat(time_value):
    """Unclear."""

    try:
        time.strptime(time_value, '%I:%M%p %Y-%m-%d')
        return True
    except ValueError:
        return False


def sep_datetime(utc_datetime):
    """Split a timespec into date and time strings."""

    if len(str(utc_datetime)) > 10:

        date_time_x = datetime.datetime.strptime(str(utc_datetime), '%Y-%m-%dT%H:%M:%S%z')
        # pst_time = time.strftime('%Y-%m-%d %H:%M', pst_time)
        date_x = str(date_time_x.day) + '/' + str(date_time_x.month) + '/' + str(date_time_x.year)
        time_x = str(date_time_x.strftime('%I')) + ':' + \
            str(date_time_x.strftime('%M')) + str(date_time_x.strftime('%p'))
    else:
        date_time_x = datetime.datetime.strptime(str(utc_datetime), '%Y-%m-%d')
        # pst_time = time.strftime('%Y-%m-%d %H:%M', pst_time)
        date_x = str(date_time_x.day) + '/' + str(date_time_x.month) + '/' + str(date_time_x.year)
        time_x = ''
    return date_x, time_x


def write_to_screen(image, sleep_seconds):
    """Write an image to the screen and sleep for requested seconds."""

    print('Writing to screen.')
    # dont remove this commented area yet
    # Write to screen
    #h_image = Image.new('1', (epd.width, epd.height), 255)
    # Open the template
    #screen_output_file = Image.open(os.path.join(picdir, image))
    # Initialize the drawing context with template as background
    #h_image.paste(screen_output_file, (0, 0))
    epd.display(epd.getbuffer(image))
    # Sleep
    print('Sleeping for ' + str(int(sleep_seconds/60)) + ' min.')
    epd.sleep()
    time.sleep(sleep_seconds)

# define function for displaying error


def display_error(error_source, color):
    """Display an error, then wait for 8 minutes."""

    print('Error in the', error_source, 'request.')
    # Initialize drawing
    error_image = Image.new('1', (epd.width, epd.height), 255)
    # Initialize the drawing
    draw = ImageDraw.Draw(error_image)
    draw.text((100, 150), error_source + ' ERROR', font=font_size(30), fill=color)
    draw.text((100, 300), 'Retrying in 8 min', font=font_size(22), fill=color)
    current_time = datetime.datetime.now().strftime('%H:%M')
    draw.text((300, 365), 'Last Refresh: ' + str(current_time), font=font_size(30), fill=color)
    # Save the error image
    error_image_file = 'error.png'
    error_image.save(os.path.join(picdir, error_image_file))
    # Close error image
    error_image.close()
    # Write error to screen
    write_to_screen(error_image_file, 8*60)
