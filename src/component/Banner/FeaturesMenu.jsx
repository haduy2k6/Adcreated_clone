// FeaturesMenu.jsx
import React from "react";
import styled from "styled-components";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faWaze } from "@fortawesome/free-brands-svg-icons";

// Styled Components
const DropdownWrapper = styled.div`
  background: white;
  border-radius: 10px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
  padding: 20px;
  display: grid;
  grid-template-columns: 2fr 1fr 1fr;
  grid-template-areas:
    "header1 header2 header3"
    "header1 header2 header4";
  gap: 35px 20px;
  z-index: 1000;
  width: 100%;
  box-sizing: border-box;
`;

const DropdownColumn = styled.div`
  grid-area: ${({ role }) => role};
  display: grid;
  grid-template-columns: ${({ items }) =>
    items.length >= 6 ? "repeat(2, 1fr)" : "1fr"};
  gap: ${({ items }) => (items.length >= 6 ? "2px 30px" : "10px")};
`;

const DropdownTitle = styled.h4`
  color: ${(props) => props.color || "#000"};
  font-weight: bolder;
  grid-column: 1 / -1;
  text-align: left;
  font-size: 13px;
`;

const DropdownItem = styled.div`
  margin-bottom: 15px;
  text-align: left;
  display: grid;
  grid-template-columns: 0.5fr 2fr 0.5fr;
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
    font-size: 12px;
    grid-area: para;
    margin: 0;
    font-weight: 520;
  }
`;

const Logo2 = styled.div`
  grid-area: logo;
  display: flex;
  align-self: start;
  justify-self: center;
`;

const CheckNew = styled.span`
  font-size: 13px;
  font-weight: bolder;
  color: green;
  border-radius: 5px;
  grid-area: new;
  align-self: start;
  justify-self: start;
  background-color: ${(props) =>
    props.$phanloai === "new" ? "#e6f9e1ff" : "#ffff"};
  padding: 2px 6px;
  visibility: ${(props) =>
    props.$phanloai === "new" ? "visible" : "hidden"};
`;

export function MyNew({ $phanloai }) {
  return <CheckNew $phanloai={$phanloai}>NEW</CheckNew>;
}

// Data
const menuData = [
  {
    title: "GENERATE",
    color: "#df277b",
    role: "header1",
    items: [
      { name: "Ad Creatives", desc: "Generate conversion-focused ad creatives", sta: "old" },
      { name: "Product Videoshoots", desc: "Text your product photos into product videoshoots", sta: "old" },
      { name: "Product Photoshoots", desc: "Elevate your product photos to stunning e-commerce visuals", sta: "old" },
      { name: "Stock Videos", desc: "Generate unique and commercially safe stock videos", sta: "old" },
      { name: "Fashion Videoshoots", desc: "Instantly create stunning fashion vodeps from any image", sta: "new" },
      { name: "Instant Ads", desc: "Generate ready-to-launch, conversion-driven ads effortlessly", sta: "new" },
      { name: "Fashion Photoshoots", desc: "Fit your product photos onto AI-generated models", sta: "old" },
      { name: "Creative Utility Suite", desc: "The all-in-one AI toolkit for every creative need", sta: "new" },
      { name: "Stock Image Generation", desc: "Generate premium stock images for all commercial uses", sta: "old" },
      { name: "Buyer Personas", desc: "Ai-powered audience profiling for precise targeting", sta: "new" },
      { name: "Text & Headlines", desc: "Generate texts high-conversion rate text", sta: "old" }
    ]
  },
  {
    title: "ANALYSE",
    color: "#df277b",
    role: "header2",
    items: [
      { name: "Creative Insights", desc: "Identify your top-performing creatives", sta: "old" },
      { name: "Competitor Insights", desc: "Gain insights from your competitors’ websites", sta: "old" },
      { name: "Compliance Checker", desc: "Check ads for brand, platform & policy compliance", sta: "new" },
      { name: "Ad Inspriation Gallery", desc: "You are one click away from your next winning ad inspriation", sta: "old" }
    ]
  },
  {
    title: "PREDICT",
    color: "#df277b",
    role: "header3",
    items: [
      { name: "Creative Scoring", desc: "Create authentic, user-generated content style ads", sta: "old" }
    ]
  },
  {
    title: "AUTOMATE",
    color: "#df277b",
    role: "header4",
    items: [
      { name: "Custom Templates", desc: "Generate creatives using the custom templates you have built" }
    ]
  }
];

const ItemTitle = styled.h5`
  grid-area: header;
  margin: 0 0 1px;
  font-size: 15px;
  font-weight: bolder;
  color: ${({ active }) => (active ?  "#df277b":"black" )};
  transition: color 0.2s ease;
`;

export default function FeaturesMenu({ maxWidth, style }) {
  return (
    <DropdownWrapper style={{ ...style, maxWidth }}
    >
      {menuData.map((col, i) => (
        <DropdownColumn key={i} items={col.items} role={col.role}>
          <DropdownTitle color={col.color}>{col.title}</DropdownTitle>
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
        </DropdownColumn>
      ))}
    </DropdownWrapper>
  );
}
