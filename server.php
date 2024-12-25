<?php

// UPLOAD PHP


class Temperature
{
    static $file = 'temp.txt';
    public static function get()
    {
        return (float)file_get_contents(self::file);
    }

    public static function update($t)
    {
        return (bool)file_put_contents(self::file, $t);
    }

}

/*

|_public_html
    temp.txt
    update.php
    Temperature.php
    .htaccess*

    *not needed
*/