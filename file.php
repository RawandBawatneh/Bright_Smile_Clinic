<?php
error_reporting(0);

$c = mysqli_connect("localhost", "root", "0569458641#2003", "ClinicManagment");

$q = "
    CREATE TABLE IF NOT EXISTS users (
        Email VARCHAR(255) NOT NULL,
        PasswordHash VARCHAR(255) NOT NULL,  
        UserType ENUM('secretary', 'Doctor') NOT NULL, 
        PRIMARY KEY (Email) 
    );
";
mysqli_query($c, $q);
?>

<?php
error_reporting(0);

if (isset($_POST['sign'])) {
    $email = $_POST['email'];
    $mypass = $_POST['pass'];
    $type = $_POST['role'];

    if ($email != "" && $mypass != "" && $type != "") {
        $c = mysqli_connect("localhost", "root", "0569458641#2003", "ClinicManagment");

        $q_check = "SELECT * FROM users WHERE Email = '$email'";
        $result = mysqli_query($c, $q_check);

        if (mysqli_num_rows($result) > 0) {
            $user = mysqli_fetch_assoc($result);

            if (password_verify($mypass, $user['PasswordHash'])) {
                echo "
                <script>
                    window.alert('Login successful!');
                    window.location.href='dashboard.html';
                </script>
                ";
            } else {
                echo "
                <script>
                    window.alert('Incorrect password!');
                    window.location.href='dashboard.html';
                </script>
                ";
            }
        } else {
            $hashedPassword = password_hash($mypass, PASSWORD_BCRYPT); 
            $q_insert = "
                INSERT INTO users(Email, PasswordHash, UserType) 
                VALUES('$email', '$hashedPassword', '$type');
            ";
            mysqli_query($c, $q_insert);

            echo "
            <script>
                window.alert('Signed up successfully!');
                window.location.href='index.html';
            </script>
            ";
        }
    } else {
        echo "
        <script>
            window.alert('Please fill all required fields!');
            window.location.href='index.html';
        </script>
        ";
    }
}
?>