<?php

// MOves files to A Directory

$targetPath = "uploads/" . basename($_FILES["inpFile"]["name"]);
move_uploaded_file($_FILES["inpFile"["tmp_name"], $targetPath)