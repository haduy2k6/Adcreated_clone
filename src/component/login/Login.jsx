import React, { useState, useRef, useEffect } from 'react';
import styled from 'styled-components';
import { HighOptions } from '../Banner/MyBanner';
import { height } from '@fortawesome/free-solid-svg-icons/fa0';

const MasterDiv = styled.section`
  display: grid;
  grid-template-columns: 1fr 1fr;
  grid-template-areas: 'left right';
  width: 100%;
  min-height: 100vh; /* Đảm bảo lấp đầy chiều cao viewport */
  box-sizing: border-box;
`;

export function SignPage() {
  return (
    <MasterDiv>
      <LoginLeft place="left" />
      <LoginRight place="right" />
    </MasterDiv>
  );
}

const Right = styled.div`
  background-color: white;
  grid-area: ${(props) => props.place || "right"};
  width: 100%;
  position: relative;
  overflow: hidden; /* Ngăn tràn ra ngoài */
  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: -14%;
    width: 140%; /* Khớp với chiều rộng của Right */
    height: 100%; /* Khớp với chiều cao của Right */
    background: url('/auth-bg.webp');
    background-size: cover; /* Giữ tỷ lệ hình ảnh */
    z-index: 1; /* Đặt phía sau nội dung */
    animation: intro-bg-animation 25s linear infinite alternate;
  }
  @keyframes intro-bg-animation {
    0% {
      transform: rotate(15deg) translateY(0);
    }
    100% {
      transform: rotate(15deg) translateY(-10%);
    }
  }
  &::after {
    z-index: 2;
    content: "";
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: linear-gradient(rgba(255, 255, 255, 0.1) 0%, rgba(255, 255, 255, 0.95) 45.07%, rgba(255, 255, 255, 0.95) 66.01%, #fff 100%);
  }
`;

const Content = styled.div`
  display: flex;
  flex-direction: column;
  gap: 2.5rem;
  width: 100%;
  position: absolute;
  z-index: 3;
  bottom: 0;
  font-family: Gilroy-Regular, sans-serif;
  font-size: 16px;
  & > .comment {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 2px;
    max-width: 576px;
    width: 70%;
    margin: 0 auto;
    text-align: center;
  }
`;

const Comment = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
  max-width: 576px;
  width: 70%;
  margin: 0 auto;
  text-align: center;
  & > * {
    margin: 0;
  }
`;

const Hero = styled.div`
  display: flex;
  flex-direction: column;
  gap: 1rem;
`;

const HeroCompanies = styled.div`
  display: flex;
  gap: 15px;
  overflow: hidden; /* Ẩn các phần tràn ra ngoài */
  gap: 15px;
  overflow: hidden; /* Ẩn các phần tràn ra ngoài */
  position: relative; /* Đảm bảo mask hoạt động đúng */
  width: 100%; /* Đảm bảo container chiếm toàn bộ chiều rộng */
  -webkit-mask-image: linear-gradient(
    to right,
    transparent 0%, /* Làm mờ bên trái */
    rgba(0, 0, 0, 1) 20%, /* Phần giữa rõ bắt đầu từ 20% */
    rgba(0, 0, 0, 1) 80%, /* Phần giữa rõ kết thúc ở 80% */
    transparent 100% /* Làm mờ bên phải */
  );
  mask-image: linear-gradient(
      to right,
      transparent 0%,
      rgba(0, 0, 0, 0.5) 20%,
      rgba(0, 0, 0, 1) 30%,
      rgba(0, 0, 0, 1) 70%,
      rgba(0, 0, 0, 0.5) 80%,
      transparent 100%
    );
`;

const Scroller = styled.div`
  display: flex;
  transition: transform 0s linear; /* Không có transition để mượt mà khi reset */
  
`;

const banHero = [];
for (let i = 1; i <= 14; i++) {
  banHero.push(`/${i}.svg`);
}

const MiniHero = styled.div`
  flex: 0 0 auto;
  width: 100px; /* Điều chỉnh theo kích thước ảnh */
  /* Bỏ margin-right vì đã có gap trên parent */
`;

function LoginRight({ place }) {
  const scrollerRef = useRef(null);

  useEffect(() => {
    const scroller = scrollerRef.current;
    if (!scroller) return;

    const speed = 0.5; // Tốc độ pixel/frame, điều chỉnh để phù hợp (nhỏ hơn để mượt)
    let animationFrame;
    let position = 0;
    let singleSetWidth = scroller.scrollWidth / 2; // Chiều rộng của một bộ (vì duplicate)

    const step = () => {
      position -= speed;
      if (position <= -singleSetWidth) {
        position = 0; // Reset về đầu để loop vô tận
      }
      scroller.style.transform = `translateX(${position}px)`;
      animationFrame = requestAnimationFrame(step);
    };

    // Bắt đầu animation sau khi mount và tính width
    const timeout = setTimeout(step, 100); // Delay nhỏ để đảm bảo width được tính

    return () => {
      cancelAnimationFrame(animationFrame);
      clearTimeout(timeout);
    };
  }, []);

  // Duplicate mảng để tạo loop seamless
  const duplicatedBanHero = [...banHero, ...banHero];

  return (
    <Right place={place}>
      <Content>
        <Comment>
          <img src="/cody.png" className="comment-avatar" />
          <h3 className="comment-name">Cody T.</h3>
          <h5 className="comment-title">Minimum Effort Maximum Attention</h5>
          <p className="comment-body">
            As one of the top real estate teams in Canada, we leverage software like Adcreative.ai
            to help deploy new dynamic ad campaigns. With the least effort of a few clicks, this tool gives you the best
            shot in getting your audience’s attention.
          </p>
        </Comment>
        <div className="trustpilot-item">
          <div className="trustpilot-stats">
            <span>500+ 5 star reviews</span>
          </div>
          <div className="trustpilot-stars">
            <img src="/g2-verified.svg" className="trustpilot-stars" />
          </div>
        </div>
        <Hero>
          <div className="hero-info" style={{ display: "flex", justifyContent: "center", alignItems: "center", gap: "1rem" }}>
            <img src="/supporting-users.png" className="Supporting Users" style={{ width: "fit-content", height: "fit-content" }} />
            <p>Supporting over <b>3,000,000 users</b> worldwide</p>
          </div>
          <div
            className="hero-info"
            style={{
              color: "#574977",
              fontWeight: "500",
              fontFamily: "Gilroy-Medium",
              fontSize: "12px",
            }}
          >
            <p>Over <b>1 Billion Ad Creatives</b> Generated by Top Brands Including:</p>
          </div>
          <HeroCompanies>
            <Scroller ref={scrollerRef}>
              {duplicatedBanHero.map((item, index) => (
                <MiniHero key={index} delay={index * 0.5}>
                  <img src={item} />
                </MiniHero>
              ))}
            </Scroller>
          </HeroCompanies>
        </Hero>
      </Content>
    </Right>
  );
}

const Form = styled.form`
  border: 1px solid white;
  border-radius: 15px;
  display: flex;
  gap: 15px;
  flex-direction: column;
  padding: 15px;
  background-color: #f4f0f5;
  min-height: 322px;
  min-width: 427px;
`;

const Button = styled.button`
  border-radius: 15px;
  padding: 21px;
  color: white;
  background-color: #df277b;
  font-size: 17px;
  font-weight: 700;
  &:hover {
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
    border-color: #df277b;
  }
`;

const Container = styled.div`
  width: 100%;
  position: relative;
  display: flex;
  align-items: center;
  flex-direction: column;
  background-color: ${({ $change }) => ($change ? '#df277b' : '#ffffff')}; /* Fixed invalid color */
  border-radius: 15px;
  padding: 1px 1px;
`;

const Input = styled.input`
  border-radius: 15px;
  padding: 20px 15px 20px 20px;
  border: 0px solid white;
  width: 92%;
  height: 100%;
  z-index: 2;
  &:focus {
    outline: none;
    border: 0px solid white;
  }
`;

const Icon = styled.div`
  z-index: 5;
  position: absolute;
  top: 20px;
  right: 20px;
  display: flex;
  align-items: center;
  justify-content: space-between; /* Fixed typo: justify-items -> justify-content */
  opacity: ${({ $change }) => ($change ? '1' : '0.5')};
  cursor: pointer; /* Added for better UX */
`;

const ParaTem = styled.p`
  display: ${({ $change }) => ($change ? 'block' : 'none')};
  position: absolute;
  top: -25px;
  left: 5%;
  overflow-wrap: normal;
  z-index: 3;
  padding: 0px 5px;
  color: ${({ $change2 }) => ($change2 ? '#df277b' : 'black')};
  background-color: ${({ $change2 }) => ($change2 ? '#e8d5de' : 'none')}; /* Fixed invalid color */
`;

const Alert = styled.span`
  width: 90%;
  left: 4%;
  border-radius: 15px;
  text-align: justify;
  color: white;
  font-size: 10px;
  font-weight: 600; /* Fixed invalid font-weight */
  display: block;
`;

function LoginLeft({ place }) {
  const [click, setClick] = useState(false);
  const [formData, setFormData] = useState({
    fullname: '',
    password: '',
    emailAddress: '',
  });
  const [nowState, setNowState] = useState({
    fullname: false,
    password: false,
    emailAddress: false,
  });
  const [error, checkError] = useState({
    fullname: false,
    password: false,
    emailAddress: false,
  });
  const [touched, setTouched] = useState(false);

  const isValidName = (name) => {
    const regex = /^[A-Za-z0-9\s\-'.]+$/;
    return regex.test(name);
  };

  const isValidMail = (mail) => {
    const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return regex.test(mail);
  };

  const isValidPass = (password) => {
    const regex = /^(?=.*[A-Z])(?=.*[!@#$%^&*])(?=.*[0-9]).{8,}$/;
    return regex.test(password);
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
    setNowState((prev) => ({
      ...prev,
      [name]: value.length > 0,
    }));
    setTouched(true);
  };

  const checkErrors = (e) => {
    const { name, value } = e.target;
    if (name === 'fullname') {
      checkError((prev) => ({
        ...prev,
        fullname: !isValidName(value),
      }));
    } else if (name === 'emailAddress') {
      checkError((prev) => ({
        ...prev,
        emailAddress: !isValidMail(value),
      }));
    } else if (name === 'password') {
      checkError((prev) => ({
        ...prev,
        password: !isValidPass(value),
      }));
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!error.fullname && !error.emailAddress && !error.password) {
      console.log('Form submitted:', formData);
      // Add API call or other submission logic here
    } else {
      console.log('Form has errors:', error);
    }
  };

  return (
    <div
      style={{
        gridArea: place,
        width: "100%",
        boxSizing: "border-box",
        display: "flex", // Thêm flexbox
        flexDirection: "column", // Sắp xếp theo cột
        alignItems: "center", // Căn giữa theo chiều ngang
        justifyContent: "center", // Căn giữa theo chiều dọc (tuỳ chọn)
        padding: "20px", // Thêm padding để tránh nội dung dính sát lề
        minWidth: "600px",
      }}
    >
      <div>
        <img src="adcreative.png" alt="ad creative" />
        <h1 style={{ color: '#df277b' }}>
          #1 most used <br /> AI tool for advertising.
        </h1>
        <p>
          Sign up today to <b>get 10 free downloads</b>
        </p>
      </div>
      <div
        className="wrapperGG"
        style={{
          padding: '15px',
          borderRadius: '15px',
          border: '1px solid white',
          backgroundColor: '#f4f0f5',
          width: "60%",
        }}
      >
        <HighOptions style={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          padding: '10px',
        }}>
          <img src="google.svg" style={{ height: '35px' }} alt="Google" />
          <p>Sign up with Google</p>
        </HighOptions>
      </div>
      <p>_________OR_________</p>
      <Form onSubmit={handleSubmit}>
        <Container $change={error.fullname}>
          <Input
            type="text"
            value={formData.fullname} // Fixed: formData.name -> formData.fullname
            placeholder={nowState.fullname ? '' : 'Full Name'}
            name="fullname"
            onChange={handleChange}
            onBlur={checkErrors}
            aria-label="Full Name"
          />
          <ParaTem $change={nowState.fullname} $change2={error.fullname}>
            Full Name
          </ParaTem>
          <Icon $change={nowState.fullname}>
            <i className="fa-solid fa-user"></i>
          </Icon>
          {touched && error.fullname && (
            <Alert>
              Name can only contain Latin letters, numbers, spaces, hyphens,
              apostrophes and periods.
            </Alert>
          )}
        </Container>

        <Container $change={error.emailAddress}>
          <Input
            type="email"
            value={formData.emailAddress}
            placeholder={nowState.emailAddress ? '' : 'Email Address'}
            name="emailAddress"
            onChange={handleChange}
            onBlur={checkErrors}
            aria-label="Email Address"
          />
          <ParaTem $change={nowState.emailAddress} $change2={error.emailAddress}>
            Email Address
          </ParaTem>
          <Icon $change={nowState.emailAddress}>
            <i className="fa-regular fa-envelope"></i>
          </Icon>
          {touched && error.emailAddress && (
            <Alert>Invalid e-mail. Use valid emails only</Alert>
          )}
        </Container>

        <Container $change={error.password}>
          <Input
            type={click ? 'text' : 'password'}
            value={formData.password}
            placeholder={nowState.password ? '' : 'Password*'}
            name="password"
            onChange={handleChange}
            onBlur={checkErrors}
            aria-label="Password"
          />
          <ParaTem $change={nowState.password} $change2={error.password}>
            Password*
          </ParaTem>
          <Icon
            $change={nowState.password}
            onClick={() => setClick((prev) => !prev)} // Fixed: Functional update
            aria-label={click ? 'Hide password' : 'Show password'}
          >
            <i className={click ? 'fa-solid fa-eye' : 'ri-eye-close-line'}></i>
          </Icon>
          {touched && error.password && (
            <Alert>
              Contain at least one uppercase letter (A-Z), special character
              <br />Be at least 8 characters long.
            </Alert>
          )}
        </Container>
        <Button type="submit" disabled={error.fullname || error.emailAddress || error.password}>
          Sign up today to get 10 free downloads
        </Button>
        <p>
          By registering you agree to our <ins><b>terms of use</b></ins>
        </p>
      </Form>
      <div
        style={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          gap: '5px',
        }}
      >
        <p>
          <b>Do you have an account?</b>
        </p>
        <p style={{ color: '#df277b', textDecoration: 'underline' }}>
          <b>Login</b>
        </p>
      </div>
    </div>
  );
}