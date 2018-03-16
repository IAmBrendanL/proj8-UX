<html>
    <head>
        <title>CIS 322 REST-api: Brevets</title>
    </head>

    <body>
        <h1>API Consumer</h1>
        <h2>List of all times</h2>
        <ul>
            <?php
            $json = file_get_contents('http://web/listAll');
            $times = json_decode($json, true);
            // function from https://stackoverflow.com/a/6413809
            array_walk_recursive($times, function ($item, $key) {
                if (($key == "close")) {
                    echo "<li>Close: $item</li>";
                } else {
                    echo "<li>Open: $item</li>";
                }
            });
            ?>
        </ul>
        <h2>List of all times as csv</h2>
        <p><?php
        // get CSV
        $results = file_get_contents('http://web/listAll/csv');
        echo nl2br($results);
        ?></p>
        <h2>List of open times</h2>
        <ul>
            <?php
            $json = file_get_contents('http://web/listOnlyOpen');
            $times = json_decode($json, true);
            array_walk_recursive($times, function ($item) {
                echo "<li>Open: $item</li>";
            });
            ?>
        </ul>
        <h2>List of close times</h2>
        <ul>
            <?php
            $json = file_get_contents('http://web/listOnlyClose');
            $times = json_decode($json, true);
            array_walk_recursive($times, function ($item) {
                echo "<li>Close: $item</li>";
            });
            ?>
        </ul>
        <h2>List of 3 times from all times</h2>
        <ul>
            <?php
            $json = file_get_contents('http://web/listAll?top=3');
            $times = json_decode($json, true);
            array_walk_recursive($times, function ($item, $key) {
                if (($key == "close")) {
                    echo "<li>Close: $item</li>";
                } else {
                    echo "<li>Open: $item</li>";
                }
            });
            ?>
        </ul>
        <h2>List of 2 open times as csv</h2>
        <p><?php
        // get CSV
        $results = file_get_contents('http://web/listOnlyOpen/csv?top=2');
        echo nl2br($results);
        ?></p>
    </body>
</html>
