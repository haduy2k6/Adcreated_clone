import React, { useState, useRef, useEffect } from "react";
import styled from "styled-components";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faChevronDown } from "@fortawesome/free-solid-svg-icons";
import FeaturesMenu from "./FeaturesMenu";
import SolutionsMenu from "./SolutionsMenu";

const Options = styled.li`
  padding: 5px 10px;
  list-style-type: none;
  color: ${(props) => (props.$home ? "#df277b" : "#383838")};
  cursor: pointer;
  position: relative;

  font-weight: 0.875rem;
    ${({ active }) =>
    (active === 'features' )&&
    `
    border-radius: 12px;
    background-color: #eae1e5;
      svg {
        transform: rotate(180deg);
        transition: transform 0.3s ease;
      }
    `}
     ${({ active2 }) =>
    (active2 === 'solutions' )&&
    `
    border-radius: 12px;
    background-color: #eae1e5;
      svg {
        transform: rotate(180deg);
        transition: transform 0.3s ease;
      }
    `}
`;

const HighOptions = styled(Options)`
  padding: 10px 25px;
  font-weight: bolder;
  display: flex;
  align-self: center;
  background-color: ${(props) =>
    props.$highoption ? "#f0dfe7ff" : "#ffffff"};
  border-radius: 12px;
  box-shadow: ${(props) =>
    props.$highoption ? "none" : "0 15px 30px -1px rgba(0, 0, 0, 0.2)"};

  &:hover {
    background-color: ${(props) =>
      props.$highoption ? "#df277b" : "#ffffff"};
    color: ${(props) => (props.$highoption ? "#ffffff" : "#383838")};
    box-shadow: 2px 19px 39px -10px #df277b;
  }
`;

const DivUl = styled.ul`
  display: flex;
  align-items: center;
  justify-items: center;
  gap: 5px;
  padding: 0;
  margin: 0;
`;

const Div = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  background-color: #fff;
  padding: 26px;
  border-radius: 15px;
  gap: 50px;
  position: fixed;
  top: 20px;
  left: 0;
  right: 0;
  margin: 0 auto;
  width: fit-content;
  box-shadow: 0 15px 30px -10px rgba(0, 0, 0, 0.2);
`;

const Image = styled.img`
  width: auto;
  height: ${(props) => (props.$google ? "27px" : "50px")};
  object-fit: contain;
`;

function MyHighOption() {
  return (
    <DivUl>
      <Options>Login</Options>
      <HighOptions $highoption={true} $home={true}>
        Try For Free Now
      </HighOptions>
      <HighOptions>
        Start Free With <Image $google={true} src="/google.svg" />
      </HighOptions>
    </DivUl>
  );
}

export default function MyBanner() {
  const sizeBanner = useRef(null);
  const featuresBtnRef = useRef(null);
  const solutionsBtnRef = useRef(null);

  const [bannerRect, setBannerRect] = useState({ width: 0, left: 0, bottom: 0 });
  const [activeMenu, setActiveMenu] = useState(null);

  // Lấy kích thước + vị trí banner khi mount và khi resize
  useEffect(() => {
    const updateRect = () => {
      if (sizeBanner.current) {
        const rect = sizeBanner.current.getBoundingClientRect();
        setBannerRect({ width: rect.width, left: rect.left, bottom: rect.bottom });
      }
    };
    updateRect();
    window.addEventListener("resize", updateRect);
    return () => window.removeEventListener("resize", updateRect);
  }, []);

  // Đóng menu khi click ra ngoài
  useEffect(() => {
    const handler = (e) => {
      if (
        featuresBtnRef.current &&
        !featuresBtnRef.current.contains(e.target) &&
        solutionsBtnRef.current &&
        !solutionsBtnRef.current.contains(e.target)
      ) {
        setActiveMenu(null);
      }
    };
    document.addEventListener("click", handler);
    return () => document.removeEventListener("click", handler);
  }, []);

  return (
    <>
      <Div ref={sizeBanner}>
        <Image src="./logoo.png" alt="logo" />
        <DivUl>
          <Options $home={true}>Home</Options>

          <Options

            ref={featuresBtnRef}
            onClick={() =>
              setActiveMenu((prev) => (prev === "features" ? null : "features"))
            }
            active={activeMenu}
          >
            Features <FontAwesomeIcon icon={faChevronDown} size="xs" />
          </Options>

          <Options
            ref={solutionsBtnRef}
            onClick={() =>
              setActiveMenu((prev) => (prev === "solutions" ? null : "solutions"))
            }
            active2={activeMenu}
          >
            Solutions <FontAwesomeIcon icon={faChevronDown} size="xs" />
          </Options>

          <Options>Enterprise</Options>
          <Options>Pricing</Options>
        </DivUl>
        <MyHighOption />
      </Div>

      {activeMenu === "features" && (
        <FeaturesMenu
          maxWidth={bannerRect.width + "px"}
          style={{
            position: "absolute",
            top: bannerRect.bottom +12+ "px",
            left: bannerRect.left + "px",
          }}
        />
      )}

      {activeMenu === "solutions" && (
        <SolutionsMenu
          maxWidth={bannerRect.width + "px"}
          style={{
            position: "absolute",
            top: bannerRect.bottom +10+ "px",
            left: bannerRect.left+150 + "px",
          }}
        />
      )}
    </>
  );
}
