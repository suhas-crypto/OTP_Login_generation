
import React, { useState } from "react";
import axios from "axios";

function App() {
  const [step, setStep] = useState(1);
  const [formData, setFormData] = useState({
    username: "",
    first_name: "",
    second_name: "",
    gender: "",
    otp: ""
  });

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleLogin = async () => {
    const res = await axios.post("http://127.0.0.1:8000/login", formData);
    alert("OTP: " + res.data.otp_for_testing);
    setStep(2);
  };

  const handleVerify = async () => {
    const res = await axios.post("http://127.0.0.1:8000/verify", {
      username: formData.username,
      otp: formData.otp
    });
    alert(res.data.message);
  };

  return (
    <div style={{ width: "300px", margin: "100px auto", textAlign: "center" }}>
      <h2>OTP Login</h2>
      {step === 1 && (
        <>
          <input name="username" placeholder="Username" onChange={handleChange} /><br/><br/>
          <input name="first_name" placeholder="First Name" onChange={handleChange} /><br/><br/>
          <input name="second_name" placeholder="Second Name" onChange={handleChange} /><br/><br/>
          <input name="gender" placeholder="Gender" onChange={handleChange} /><br/><br/>
          <button onClick={handleLogin}>Generate OTP</button>
        </>
      )}
      {step === 2 && (
        <>
          <input name="otp" placeholder="Enter OTP" onChange={handleChange} /><br/><br/>
          <button onClick={handleVerify}>Verify OTP</button>
        </>
      )}
    </div>
  );
}

export default App;
