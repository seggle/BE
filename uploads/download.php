<?php
	$dir1 = $_GET['dir1'];
	$dir2 = $_GET['dir2'];
	$file = $_GET['file'];
	$down = $dir1.'/'.$dir2.'/'.$file;
	// echo $down;
	$filesize = filesize($down);
	if(isset($_GET['dir1']) && isset($_GET['dir2']) && isset($_GET['file'])) {
		if(file_exists($down)) {
			header("Content-Type:application/octet-stream");
			header("Content-Disposition:attachment;filename=$file");
			header("Content-Transfer-Encoding:binary");
			header("Content-Length:".$filesize);
			header("Cache-Control:cache,must-revalidate");
			header("Pragma:no-cache");
			header("Expires:0");
			if(is_file($down)) {
				$fp = fopen($down, "r");
				while(!feof($fp)) {
					$buf = fread($fp,8096);
					$read = strlen($buf);
					print($buf);
					flush();
				}
			}
		} else {
			echo '존재하지 않는 파일입니다.';
		}
	} else {
		echo '존재하지 않는 파일입니다.';
	}
?>