import React, { useState } from "react";
import styled from "styled-components";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faWaze } from "@fortawesome/free-brands-svg-icons";
import { MyNew } from "./FeaturesMenu";

const DropWrapper = styled.div`
  background: white;
  border-radius: 10px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
  padding: 15px 35px;
  display: grid;
  grid-template-columns: repeat(2, minmax(250px, 1fr));
  grid-template-areas:
    "header1 header2"
    "header3 header2";
  gap: 15px 15px;
  z-index: 1000;
  width: fit:content;
  box-sizing: border-box;
`;

const DropColumn = styled.div`
  grid-area: ${({ role }) => role};
  padding-right: 20px;
  padding-bottom: 20px;
  box-sizing: border-box;
`;

const Banner = styled.img`
  grid-area: header2;
  border-radius: 12px;
  object-fit: contain;
  justify-self: center;
  align-self: center;
  height: 300px;
`;

const DropTitle = styled.h1`
  font-size: 16px;
  color:  ${({ color }) => color};
  text-align: left;
  width: max-content;
  transition: color 0.2s ease;
`;

const Logo2 = styled.div`
  grid-area: logo;
  display: flex;
  align-self: start;
  justify-self: center;
`;

const DropdownItem = styled.div`
  margin-bottom: 15px;
  text-align: left;
  display: grid;
  grid-template-columns: 0.5fr 1fr 1fr;
  grid-template-areas:
    "logo header new"
    "logo para   para";

  h5 {
    grid-area: header;
    margin: 0 0 1px;
    font-size: 15px;
    font-weight: bolder;
    color: #333;
  }
  &: hover  .myH5, &:hover svg{
    color:#df277b;
  }
  .myH5,svg {
    transition: color 0.3s ease;
    color: black;
  }
  p {
    grid-area: para;
    margin: 0;
    font-weight: 520;
    width: max-content;
  }
`;

const menuData = [
  {
    title: "ADCREATIVE.AI FOR",
    color: "#df277b",
    role: "header1",
    items: [
      { name: "Small Business", desc: "Boost sales with instant ads", sta: "old" },
      { name: "E-Commerce", desc: "Convert shoppers into buyers", sta: "old" },
      { name: "Agency", desc: "Scale client campaigns effortlessly", sta: "old" }
    ]
  },
  {
    title: "ESTIMATE YOUR PROFIT",
    color: "#df277b",
    role: "header3",
    items: [
      { name: "ROI Calculator", desc: "See your profit before you spend", sta: "new" }
    ]
  }
];


export default function SolutionsMenu({ maxWidth, style }) {
  const [hoverPos, setHoverPos] = useState({ i: null, j: null });

  return (
    <DropWrapper style={{ ...style, maxWidth }}>
      {menuData.map((col, i) => (
        <DropColumn
          key={i}
          role={col.role}
        >
          <DropTitle color={col.color}>{col.title}</DropTitle>

          {col.items.map((item, j) => (
            <DropdownItem key={j}>
              <Logo2>
                <FontAwesomeIcon icon={faWaze} size="lg" />
              </Logo2>
                <h5 className="myH5">{item.name}</h5>
              <MyNew $phanloai={item.sta} />
              <p>{item.desc}</p>
            </DropdownItem>
          ))}
        </DropColumn>
      ))}
      <Banner src="/check.png" alt="logo" />
    </DropWrapper>
  );
}
