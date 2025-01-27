wifi_form_styles = """
<style>
     body {{ font-family: Arial, sans-serif; background-color: #f2f2f2; }}
            .container {{ width: 50%; margin: auto; background-color: #fff; padding: 20px; border-radius: 5px; }}
            input[type=text], input[type=password] {{
                width: 100%;
                padding: 12px 20px;
                margin: 8px 0;
                display: inline-block;
                border: 1px solid #ccc;
                border-radius: 4px;
                box-sizing: border-box;
            }}
            input[type=submit] {{
                width: 100%;
                background-color: #4CAF50;
                color: white;
                padding: 14px 20px;
                margin: 8px 0;
                border: none;
                border-radius: 4px;
                cursor: pointer;
            }}
            input[type=submit]:hover {{
                background-color: #45a049;
            }}
            .status {{ background-color: #e7f3fe; border-left: 6px solid #2196F3; padding: 10px; }}
</style>
"""

config_page_styles = """
<style>
        body {{ font-family: Arial, sans-serif; background-color: #f2f2f2; }}
            .container {{ width: 60%; margin: auto; background-color: #fff; padding: 20px; border-radius: 5px; }}
            input[type=text], input[type=number] {{
                width: 100%;
                padding: 12px 20px;
                margin: 8px 0;
                display: inline-block;
                border: 1px solid #ccc;
                border-radius: 4px;
                box-sizing: border-box;
            }}
            input[type=checkbox] {{
                margin: 8px 0;
            }}
            input[type=submit] {{
                width: 100%;
                background-color: #4CAF50;
                color: white;
                padding: 14px 20px;
                margin: 8px 0;
                border: none;
                border-radius: 4px;
                cursor: pointer;
            }}
            input[type=submit]:hover {{
                background-color: #45a049;
            }}
            .status {{ background-color: #e7f3fe; border-left: 6px solid #2196F3; padding: 10px; margin-bottom: 20px; }}
            .status p {{ margin: 5px 0; }}

    label, a{{
  cursor: pointer;
  user-select: none;
  text-decoration: none;
  display: inline-block;
  color: inherit;
  transition: border 0.2s;
  border-bottom: 5px solid rgba(#8e44ad, 0.2);
  padding: 3px 2px;
  &:hover{{
    border-bottom-color: #9b59b6;
  }}
}

.layout{{
  display: grid;
  height: 100%;
  width: 100%;
  overflow: hidden;
  grid-template-rows: 50px 1fr;
  grid-template-columns: 1fr 1fr 1fr;
}}

input[type="radio"]{{
  display: none;
}}

label.nav{{
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  border-bottom: 2px solid #8e44ad;
  background: #ecf0f1;
  user-select: none;
  transition: background 0.4s, padding-left 0.2s;
  padding-left: 0;
  input[type="radio"]:checked + .page + &{{
    background: #9b59b6;
    color: #ffffff;
    padding-left: 20px;
    span{{
      padding-left: 20px  
    }}
    svg{{
      opacity: 1;
    }}
  }}
  span{{
    padding-left: 0px;
    position: relative;
  }}
  svg{{
    left: 0;
    top: -3px;
    position: absolute;
    width: 15px;
    opacity: 0;
    transition: opacity 0.2s;
  }}
}}

.page{{
  grid-column-start: 1;
  grid-row-start: 2;
  grid-column-end: span 3;
  padding: 0px 20px;
  display: flex;
  align-items: center;
}}

.page-contents > *{{
  opacity: 0;
  transform: translateY(20px);
  transition: opacity 0.2s, transform 0.2s;
  @for $c from 1 through 20{{
    &:nth-child(#{{$c}}){{
      transition-delay: 0.2s + ($c * 0.2s);
    }}
  }}
}}

input[type="radio"] + .page{{
  transition: transform 0.2s;
  transform: translateX(100%);
}}

input[type="radio"]:checked + .page{{
  transform: translateX(0%);
  .page-contents > *{{
    opacity: 1;
    transform: translateY(0px);
  }}
}}

.page-contents{{
  max-width: 100%;
  width: 500px;
  margin: 0 auto;
}}

</style>
"""