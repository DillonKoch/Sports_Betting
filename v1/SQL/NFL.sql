select *
from NFL_ESPN
left join NFL_ESB on NFL_ESPN.datetime = NFL_ESB.datetime and ((NFL_ESPN.Home = NFL_ESB.Home) or (NFL_ESPN.Home = NFL_ESB.Away))
left join NFL_WH on NFL_ESPN.datetime = NFL_WH.datetime and ((NFL_ESPN.Home = NFL_WH.Home) or (NFL_ESPN.Home = NFL_WH.Away))
left join NFL_Odds on NFL_ESPN.datetime = NFL_Odds.datetime and ((NFL_ESPN.Home = NFL_Odds.Home) or (NFL_ESPN.Home = NFL_Odds.Away))
