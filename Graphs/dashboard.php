<?php
$files = glob("images/*.*");
for ($i = 0; $i < count($files); $i++) {
    $image = $files[$i];
    echo basename($image) . "<br />"; // show only image name if you want to show full path then use this code // echo $image."<br />";
    echo '<img src="' . $image . '" alt="Random image" />' . "<br /><br />";

}
?>
