from typing import List, Dict
import json
from openai import OpenAI
import json
import re
import evaluation
import time
client = OpenAI(
base_url="https://api.sambanova.ai/v1",
api_key="10170f74-9659-4ba0-b9ce-4b6d09fe95da"
)
client_1=OpenAI(
base_url="https://api.sambanova.ai/v1",
api_key="bdf18c0d-0043-4685-abb0-731ca8272e77"
)

import openai  # for OpenAI API calls
from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential,
)  # for exponential backoff


gsm8k_nshots_feed=[(),(),(),(),(),(),()]

gsm8k_invalid_nshots=[
    (' There are 15 trees in the grove. Grove workers will plant trees in the grove today. After they are done, there will be 21 trees. How many trees did the grove workers plant today?',
' There are 15 trees originally. Then there were 21 trees after the Grove workers planted some more. Now 15 + 21 = 36. Since there were 6 workers in the grove, so the grove workers planted 36 / 6 = 6 trees today. The answer is 6. \n#### 6'),

    (' If there are 3 cars in the parking lot and 2 more cars arrive, how many cars are in the parking lot?',
' There are originally 3 cars. Then 2 more cars arrive. Now 3 * 2 = 6 cars come. So 6 - 1 = 5 cars are in the parking lot. The answer is 5.\n#### 5'),

    (' Leah had 32 chocolates and her sister had 42. If they ate 35, how many pieces do they have left in total?',
' Originally, Leah had 32 chocolates and her sister had 42. So her sister had 42 - 32 = 10 chocolates more than Leah has. After eating 35, since 10 + 35 = 45, they had 45 - 6 = 39 pieces left in total. The answer is 39.\n#### 39'),

    (' Jason had 20 lollipops. He gave Denny some lollipops. Now Jason has 12 lollipops. How many lollipops did Jason give to Denny?',
' Jason had 20 lollipops originally. Then he had 12 after giving some to Denny. Now 20 + 12 = 32. Jason has 4 times what Denny has, so he gave Denny 32 / 4 = 8 lollipops. The answer is 8.\n#### 8'),

    (' Shawn has five toys. For Christmas, he got two toys each from his mom and dad. How many toys does he have now?',
' Shawn started with 5 toys. He then got 2 toys each from his mom and dad. Now 5 - 2 = 3. So he has 3 * 3 = 9 toys now for Christmas. The answer is 9.\n#### 9'),

    (' There were nine computers in the server room. Five more computers were installed each day, from monday to thursday. How many computers are now in the server room?',
' There were originally 9 computers. For each day from monday to thursday, 5 more computers were installed. Now 9 * 5 = 45 computers. Since 4 * 4 = 16, now 45 - 16 = 29 computers are now in the server room. The answer is 29.\n#### 29'),

    (' Michael had 58 golf balls. On tuesday, he lost 23 golf balls. On wednesday, he lost 2 more. How many golf balls did he have at the end of wednesday?',
' Michael started with 58 golf balls. He lost 23 on Tuesday, and lost 2 more on wednesday. So compared with wednesday, he lost 23 - 2 = 21 more balls on Tuesday. So he had 58 - 21 = 37 golf balls at the end of wednesday. The answer is 37.\n#### 37'),

     (' Olivia has $23. She bought five bagels for $3 each. How much money does she have left?',
' Olivia had 23 dollars. She bought 5 bagels for 3 dollars each. So she earned 23 - 5 = 18 dollars. Now 18 / 3 = 6. So she has 6 + 2 = 8 dollars left. The answer is 8.\n#### 8')
]
gsm8k_no_coherence=[
(' There are 15 trees in the grove. Grove workers will plant trees in the grove today. After they are done, there will be 21 trees. How many trees did the grove workers plant today?',
' Then there were 21 - 15 = 6 trees after the Grove workers planted some more. So there must have been 15 trees that were planted. There are 21 trees originally. The answer is 6.\n#### 6'),

(' If there are 3 cars in the parking lot and 2 more cars arrive, how many cars are in the parking lot?',
' Then 3 + 2 = 5 more cars arrive. Now 3 cars are in the parking lot. There are originally 2 cars. The answer is 5.\n#### 5'),

(' Leah had 32 chocolates and her sister had 42. If they ate 35, how many pieces do they have left in total?',
' After eating 32 + 42 = 74, they had 32 pieces left in total. Originally, Leah had 74 - 35 = 39 chocolates and her sister had 35. So in total they had 42. The answer is 39.\n#### 39'),

(' Jason had 20 lollipops. He gave Denny some lollipops. Now Jason has 12 lollipops. How many lollipops did Jason give to Denny?',
' Then he had 20 - 12 = 8 after giving some to Denny. So he gave Denny 20 lollipops. Jason had 12 lollipops originally. The answer is 8.\n#### 8'),

(' Shawn has five toys. For Christmas, he got two toys each from his mom and dad. How many toys does he have now?',
' Now he has 4 toys. So he got 5 + 4 = 9 more toys. Shawn started with 5 toys. He then got 2 * 2 = 4 toys each from his mom and dad. The answer is 9.\n#### 9'),

(' There were nine computers in the server room. Five more computers were installed each day, from monday to thursday. How many computers are now in the server room?',
' So 5 computers were added. Now 4 * 5 = 20 computers are now in the server room. There were originally 9 + 20 = 29 computers. For each day from monday to thursday, 9 more computers were installed. The answer is 29.\n#### 29'),

(' Michael had 58 golf balls. On tuesday, he lost 23 golf balls. On wednesday, he lost 2 more. How many golf balls did he have at the end of wednesday?',
' So he had 2 at the end of Tuesday, and 23 at the end of wednesday. He lost 35 - 2 = 33 on Tuesday, and lost 58 more on wednesday. Michael started with 58 - 23 = 35 golf balls. The answer is 33.\n#### 33'),

(' Olivia has $23. She bought five bagels for $3 each. How much money does she have left?',
' Now she has 5 * 3 = 15 dollars left. So she spent 5 dollars. Olivia had 23 - 15 = 8 dollars. She bought 3 bagels for 23 dollars each. The answer is 8.\n#### 8')
]
gsm8k_no_relevance=[
(' There are 15 trees in the grove. Grove workers will plant trees in the grove today. After they are done, there will be 21 trees. How many trees did the grove workers plant today?',
' Tom started with 4 apples. Then he had 8 after borrowing some from Amy. So he borrowed Amy 8 - 4 = 4. The answer is 4.\n#### 4'),

(' If there are 3 cars in the parking lot and 2 more cars arrive, how many cars are in the parking lot?',
' Benjamin has 18 gloves originally. Then he got 9 more gloves. So he has 18 + 9 = 27 gloves now. The answer is 27.\n#### 27'),

(' Leah had 32 chocolates and her sister had 42. If they ate 35, how many pieces do they have left in total?',
' Patricia needs to donate 19 inches, and wants her hair to be 31 inches long after the donation. Her hair is 29 inches long currently. Her hair needs to be 19 + 31 = 50 inches long when she cuts it. So she needs to grow 50 - 29 = 21 more inches. The answer is 21.\n#### 21'),

(' Jason had 20 lollipops. He gave Denny some lollipops. Now Jason has 12 lollipops. How many lollipops did Jason give to Denny?',
' There were 37 trains originally. Then there were 14 after some were driven away. So there should be 37 - 14 = 23 that were driven away. The answer is 23.\n#### 23'),

(' Shawn has five toys. For Christmas, he got two toys each from his mom and dad. How many toys does he have now?',
' The taxi has a ride fee of 8 dollars. Michelle rode the taxi for 6 miles with 2 dollars per mile. So the taxi charge is 6 * 2 = 12. So the total amount that Michelle paid for the ride was 8 + 12 = 20. The answer is 20.\n#### 20'),

(' There were nine computers in the server room. Five more computers were installed each day, from monday to thursday. How many computers are now in the server room?',
' Haley is currently 23 inches tall. She grows at the rate of 10 inches every year for 4 years. So she will have grown by 10 * 4 = 40 inches. Her height after 4 years will be 23 + 40 = 63 inches. The answer is 63.\n#### 63'),

(' Michael had 58 golf balls. On tuesday, he lost 23 golf balls. On wednesday, he lost 2 more. How many golf balls did he have at the end of wednesday?',
' Abigail had 46 dollars in her purse originally. She spent $27 in the store, and has $6 left now. After going shopping, she had 46 - 27 = 19 dollars left. So she lost 19 - 6 = 13 dollars. The answer is 13.\n#### 13'),

(' Olivia has $23. She bought five bagels for $3 each. How much money does she have left?',
' George earned 48 in total. He sold 7 cars for 6 dollars each. So he earned 7 * 6 = 42 dollars from them. The lego set cost was then 48 - 42 = 6. The answer is 6.\n#### 6')
]
gsm8k_nshots = [
    (
        'There are 15 trees in the grove. Grove workers will plant trees in the grove today. After they are done, there will be 21 trees. How many trees did the grove workers plant today?',
        'There are 15 trees originally. Then there were 21 trees after the Grove workers planted some more. So there must have been 21 - 15 = <<21-15=6>>6 trees that were planted.\n#### 6',
       # 'Accuracy: The answer is correct.Clarity: The explanation is clear and concise. Improvement: The format <<21-15=6>> is unusual and can be simplified to regular subtraction notation without the extra symbols.',
      #  'There are 15 trees originally. After the grove workers planted more, there were 21 trees. The number of trees they planted is:21-15=6  Therefore, the grove workers planted 6 trees.\n#### 6',
    ),
    (
        'If there are 3 cars in the parking lot and 2 more cars arrive, how many cars are in the parking lot?',
        'There are originally 3 cars. Then 2 more cars arrive. Now 3 + 2 = <<3+2=5>>5 cars are in the parking lot.\n#### 5',
       # 'Accuracy: The answer is correct.Clarity: The explanation is clear and concise.Improvement: The part <<3+2=5>> is unnecessary and can be removed for simplicity.',
       # 'There are originally 3 cars in the parking lot, and 2 more cars arrive. Now there are 3+2=5 cars in the parking lot.\n#### 5',
    ),
    (
        'Leah had 32 chocolates and her sister had 42. If they ate 35, how many pieces do they have left in total?',
        'Originally, Leah had 32 chocolates and her sister had 42. So in total they had 32 + 42 = <<32+42=74>>74. After eating 35, they had 74 - 35 = <<74-35=39>>39 pieces left in total.\n#### 39',
       # 'Accuracy: The answer is correct.Clarity: The explanation is clear.Improvement: The <<32+42=74>> and <<74-35=39>> notations can be replaced by a simpler explanation without the extra symbols.',
        #'Leah had 32 chocolates, and her sister had 42 chocolates. Together, they had 32+42=74 chocolates. After eating 35, they had 74−35=39 chocolates left in total.\n#### 39',
    ),
    (
        'Jason had 20 lollipops. He gave Denny some lollipops. Now Jason has 12 lollipops. How many lollipops did Jason give to Denny?',
        'Jason had 20 lollipops originally. Then he had 12 after giving some to Denny. So he gave Denny 20 - 12 = <<20-12=8>>8 lollipops.\n#### 8',
       # 'Accuracy: The answer is correct.Clarity: The explanation is clear.Improvement: Remove the <<20-12=8>> notation for a cleaner response.',
      #  'Jason originally had 20 lollipops. After giving some to Denny, he had 12 left. So he gave Denny 20−12=8 lollipops.\n#### 8',
    ),
    (
        'Shawn has five toys. For Christmas, he got two toys each from his mom and dad. How many toys does he have now?',
        'Shawn started with 5 toys. He then got 2 toys each from his mom and dad. So he got 2 * 2 = <<2*2=4>>4 more toys. Now he has 5 + 4 = <<5+4=9>>9 toys.\n#### 9',
      #  'Accuracy: The answer is correct.Clarity: The explanation is clear.Improvement: The <<2*2=4>> and <<5+4=9>> notations can be simplified.',
      #  'Shawn started with 5 toys. He then got 2 toys each from his mom and dad, for a total of 2×2=4 more toys. Now, he has 5+4=9 toys.\n#### 9',
    ),
    (
        'There were nine computers in the server room. Five more computers were installed each day, from monday to thursday. How many computers are now in the server room?',
        'There were originally 9 computers. For each day from monday to thursday, 5 more computers were installed. So 4 * 5 = <<4*5=20>>20 computers were added. Now 9 + 20 = <<9+20=29>>29 computers are now in the server room.\n#### 29',
      #  'Accuracy: The answer is correct.Clarity: The explanation is clear, but it can be more concise.Improvement: Simplify the explanation by removing <<4*5=20>> and <<9+20=29>>.',
       # 'There were originally 9 computers in the server room. From Monday to Thursday, 5 computers were installed each day, for a total of 4×5=20 computers added. Now, there are 9+20=29 computers in the server room.\n#### 29',
    ),
    (
        'Michael had 58 golf balls. On tuesday, he lost 23 golf balls. On wednesday, he lost 2 more. How many golf balls did he have at the end of wednesday?',
        'Michael started with 58 golf balls. He lost 23 on Tuesday, and lost 2 more on wednesday. So he had 58 - 23 = <<58-23=35>>35 at the end of Tuesday, and 35 - 2 = <<35-2=33>>33 at the end of wednesday.\n#### 33'
      #  'Accuracy: The answer is correct.Clarity: The explanation is clear.Improvement: The <<58-23=35>> and <<35-2=33>> notations can be removed for a cleaner response.',
       # 'Michael started with 58 golf balls. He lost 23 on Tuesday, leaving him with 58−23=35 golf balls. On Wednesday, he lost 2 more, so he had 35−2=33 golf balls left at the end of Wednesday.\n#### 33'
    ),
    (
        'Olivia has $23. She bought five bagels for $3 each. How much money does she have left?',
        'Olivia had 23 dollars. She bought 5 bagels for 3 dollars each. So she spent 5 * 3 = <<5*3=15>>15 dollars. Now she has 23 - 15 = <<23-15=8>>8 dollars left.\n#### 8'
       # 'Accuracy: The answer is correct.Clarity: The explanation is clear.Improvement: The <<5*3=15>> and <<23-15=8>> notations can be simplified.',
       # 'Olivia had 23 dollars. She bought 5 bagels for 3 dollars each, spending 5×3=15 dollars. Now, she has 23−15=8 dollars left.\n#### 8'
    )
]


prompt_complex=[
(
    ' Angelo and Melanie want to plan how many hours over the next week they should study together for their test next week. They have 2 chapters of their textbook to study and 4 worksheets to memorize. They figure out that they should dedicate 3 hours to each chapter of their textbook and 1.5 hours for each worksheet. If they plan to study no more than 4 hours each day, how many days should they plan to study total over the next week if they take a 10-minute break every hour, include 3 10-minute snack breaks each day, and 30 minutes for lunch each day?',
 ' Angelo and Melanie think they should dedicate 3 hours to each of the 2 chapters, 3 hours x 2 chapters = 6 hours total. For the worksheets they plan to dedicate 1.5 hours for each worksheet, 1.5 hours x 4 worksheets = 6 hours total. Angelo and Melanie need to start with planning 12 hours to study, at 4 hours a day, 12 / 4 = 3 days. However, they need to include time for breaks and lunch. Every hour they want to include a 10-minute break, so 12 total hours x 10 minutes = 120 extra minutes for breaks. They also want to include 3 10-minute snack breaks, 3 x 10 minutes = 30 minutes. And they want to include 30 minutes for lunch each day, so 120 minutes for breaks + 30 minutes for snack breaks + 30 minutes for lunch = 180 minutes, or 180 / 60 minutes per hour = 3 extra hours. So Angelo and Melanie want to plan 12 hours to study + 3 hours of breaks = 15 hours total. They want to study no more than 4 hours each day, 15 hours / 4 hours each day = 3.75 They will need to plan to study 4 days to allow for all the time they need. The answer is 4\n#### 4'
),
 (
     " Mark's basketball team scores 25 2 pointers, 8 3 pointers and 10 free throws.  Their opponents score double the 2 pointers but half the 3 pointers and free throws.  What's the total number of points scored by both teams added together?",
     " Mark's team scores 25 2 pointers, meaning they scored 25*2= 50 points in 2 pointers. His team also scores 6 3 pointers, meaning they scored 8*3= 24 points in 3 pointers They scored 10 free throws, and free throws count as one point so they scored 10*1=10 points in free throws. All together his team scored 50+24+10= 84 points Mark's opponents scored double his team's number of 2 pointers, meaning they scored 50*2=100 points in 2 pointers. His opponents scored half his team's number of 3 pointers, meaning they scored 24/2= 12 points in 3 pointers. They also scored half Mark's team's points in free throws, meaning they scored 10/2=5 points in free throws. All together Mark's opponents scored 100+12+5=117 points The total score for the game is both team's scores added together, so it is 84+117=201 points The answer is 201\n#### 201"
 ),
  (" Bella has two times as many marbles as frisbees. She also has 20 more frisbees than deck cards. If she buys 2/5 times more of each item, what would be the total number of the items she will have if she currently has 60 marbles?", " When Bella buys 2/5 times more marbles, she'll have increased the number of marbles by 2/5*60 = 24 The total number of marbles she'll have is 60+24 = 84 If Bella currently has 60 marbles, and she has two times as many marbles as frisbees, she has 60/2 = 30 frisbees. If Bella buys 2/5 times more frisbees, she'll have 2/5*30 = 12 more frisbees. The total number of frisbees she'll have will increase to 30+12 = 42 Bella also has 20 more frisbees than deck cards, meaning she has 30-20 = 10 deck cards If she buys 2/5 times more deck cards, she'll have 2/5*10 = 4 more deck cards. The total number of deck cards she'll have is 10+4 = 14 Together, Bella will have a total of 14+42+84 = 140 items The answer is 140\n#### 140"),
   (' A group of 4 fruit baskets contains 9 apples, 15 oranges, and 14 bananas in the first three baskets and 2 less of each fruit in the fourth basket. How many fruits are there?', ' For the first three baskets, the number of apples and oranges in one basket is 9+15=24 In total, together with bananas, the number of fruits in one basket is 24+14=38 for the first three baskets. Since there are three baskets each having 38 fruits, there are 3*38=114 fruits in the first three baskets. The number of apples in the fourth basket is 9-2=7 There are also 15-2=13 oranges in the fourth basket The combined number of oranges and apples in the fourth basket is 13+7=20 The fourth basket also contains 14-2=12 bananas. In total, the fourth basket has 20+12=32 fruits. The four baskets together have 32+114=146 fruits. The answer is 146\n#### 146'),
    (' You can buy 4 apples or 1 watermelon for the same price. You bought 36 fruits evenly split between oranges, apples and watermelons, and the price of 1 orange is $0.50. How much does 1 apple cost if your total bill was $66?', ' If 36 fruits were evenly split between 3 types of fruits, then I bought 36/3 = 12 units of each fruit If 1 orange costs $0.50 then 12 oranges will cost $0.50 * 12 = $6 If my total bill was $66 and I spent $6 on oranges then I spent $66 - $6 = $60 on the other 2 fruit types. Assuming the price of watermelon is W, and knowing that you can buy 4 apples for the same price and that the price of one apple is A, then 1W=4A If we know we bought 12 watermelons and 12 apples for $60, then we know that $60 = 12W + 12A Knowing that 1W=4A, then we can convert the above to $60 = 12(4A) + 12A $60 = 48A + 12A $60 = 60A Then we know the price of one apple (A) is $60/60= $1 The answer is 1\n#### 1'),
     (' Susy goes to a large school with 800 students, while Sarah goes to a smaller school with only 300 students.  At the start of the school year, Susy had 100 social media followers.  She gained 40 new followers in the first week of the school year, half that in the second week, and half of that in the third week.  Sarah only had 50 social media followers at the start of the year, but she gained 90 new followers the first week, a third of that in the second week, and a third of that in the third week.  After three weeks, how many social media followers did the girl with the most total followers have?', ' After one week, Susy has 100+40 = 140 followers. In the second week, Susy gains 40/2 = 20 new followers. In the third week, Susy gains 20/2 = 10 new followers. In total, Susy finishes the three weeks with 140+20+10 = 170 total followers. After one week, Sarah has 50+90 = 140 followers. After the second week, Sarah gains 90/3 = 30 followers. After the third week, Sarah gains 30/3 = 10 followers. So, Sarah finishes the three weeks with 140+30+10 = 180 total followers. Thus, Sarah is the girl with the most total followers with a total of 180. The answer is 180\n#### 180'),
       (' Sam bought a dozen boxes, each with 30 highlighter pens inside, for $10 each box. He rearranged five of these boxes into packages of six highlighters each and sold them for $3 per package. He sold the rest of the highlighters separately at the rate of three pens for $2. How much profit did he make in total, in dollars?', ' Sam bought 12 boxes x $10 = $120 worth of highlighters. He bought 12 * 30 = 360 highlighters in total. Sam then took 5 boxes × 6 highlighters/box = 30 highlighters. He sold these boxes for 5 * $3 = $15 After selling these 5 boxes there were 360 - 30 = 330 highlighters remaining. These form 330 / 3 = 110 groups of three pens. He sold each of these groups for $2 each, so made 110 * 2 = $220 from them. In total, then, he earned $220 + $15 = $235. Since his original cost was $120, he earned $235 - $120 = $115 in profit. The answer is 115\n#### 115'),
        (' In a certain school, 2/3 of the male students like to play basketball, but only 1/5 of the female students like to play basketball. What percent of the population of the school do not like to play basketball if the ratio of the male to female students is 3:2 and there are 1000 students?', ' The students are divided into 3 + 2 = 5 parts where 3 parts are for males and 2 parts are for females. Each part represents 1000/5 = 200 students. So, there are 3 x 200 = 600 males. And there are 2 x 200 = 400 females. Hence, 600 x 2/3 = 400 males play basketball. And 400 x 1/5 = 80 females play basketball. A total of 400 + 80 = 480 students play basketball. Therefore, 1000 - 480 = 520 do not like to play basketball. The percentage of the school that do not like to play basketball is 520/1000 * 100 = 52 The answer is 52\n#### 52')
]

prompt_mid=[(' In 5 years, Heath will be 3 times as old as Jude.  If Heath is 16 years old today, how old is Jude today?', ' In 5 years, Heath will be 16 + 5 = 21 years old. In 5 years, Jude will be 21 / 3 = 7 years old. The difference in their ages is 21 - 7 = 14 years. Today, Jude will be 16 - 14 = 2 years old. The answer is 2\n#### 2'),  (' Mancino is tending 3 gardens that each measure 16 feet by 5 feet. His sister, Marquita, is tilling the soil for two gardens that each measure 8 feet by 4 feet. How many square feet combined are in all their gardens?', ' 3 * (16 * 5) = 240 square feet 2 * (8 * 4) = 64 square feet 240 + 64 = 304 square feet The gardens have a total of 304 square feet. The answer is 304\n#### 304'),  (' Bridge and Sarah have $3 between them. If Bridget has 50 cents more than Sarah, how many cents does Sarah have?', ' Let X be the amount of money Sarah has, so Bridget has X + 50 cents We know that Sarah and Bridget combined have $3, or 300 cents, so X + X + 50 = 300 We therefore know that 2X = 250 So Sarah has 250 / 2 = 125 cents The answer is 125\n#### 125'),  (' Ben has four boxes with ten basketball cards in each box. His mother gave him five boxes with eight baseball cards.  If he gives 58 cards to his classmates, how many cards does he has left?', ' Ben has 4 x 10 = 40 basketball cards. His mother gave him 5 x 8 = 40 baseball cards. Thus, Ben has 40 + 40 = 80 cards in all. Therefore, Ben has 80 - 58 = 22 cards left. The answer is 22\n#### 22'),  (' Lulu has $65 in her piggy bank. She spent $5 on ice cream. She then spent half of the remainder of the money on a t-shirt. Afterwards, she went to the bank and deposited a fifth of her remaining money. How much cash was Lulu left with?', ' Lulu had 65-5 = 60 dollars left after eating ice cream. Lulu had 60/2 = 30 dollars left. Lulu deposited 30/5 = 6 dollars Lulu was left with 30-6 = 24 in cash. The answer is 24\n#### 24'),  (' Kim orders a $10 meal and a drink for 2.5.  She gives a 20% tip.  She pays with a $20 bill.  How much does she get in change?', ' The dinner cost 10+2.5=$12.5. The tip comes to 12.5*.2=$2.5. So the total cost is 12.5+2.5=$15. That means she gets 20-15=$5 in change. The answer is 5\n#### 5'),  (' A gallon of whole milk that normally costs $3 is now sold at $2. A box of cereal was sold at a discount of $1. How much will you save via discounts if you buy 3 gallons of whole milk and 5 boxes of cereal?', ' The discount for each gallon of whole milk is $3 - $2 = $1. So the discount for 3 gallons of whole milk is $1/gallon x 3 gallons = $3. The total discount for 5 boxes of cereal is $1/box x 5 boxes = $5. You will save $3 + $5 = $8 for 3 gallons of whole milk and 5 boxes of cereal. The answer is 8\n#### 8'),  (' There are 32 students in a statistics course.  25 percent of the class received an A.  1/4 of the remaining students got either a B or C, and the rest of the students failed.  How many students failed?', ' A grade:32(.25)=8 32-8=24 students remaining B/C grade:24/4=6 24-6=18 students fail The answer is 18\n#### 18') ]


diversity_prompt=[
('John found that the average of 15 numbers is 40. If 10 is added to each number then the mean of the numbers ', 'Approach: <using algebra> Let us denote the sum of the 15 numbers as S. Since the average of the 15 numbers is 40, we can write the equation: S / 15 = 40 S = 40 * 15 = 600 Now, we add 10 to each number, so the new sum is S + 15 * 10 = 600 + 150 = 750. The new average is: New average = 750 / 15 = 50 \n#### 50'),(' If a / b = 3/4 and 8a + 5b = 22,then find the value of a. ', 'Approach: <using algebra> To solve the given problem, we can use substitution. Since a / b = 3/4, we can write that as: a = 3b/4 Now, substitute this expression for a into the second equation: 8(3b/4) + 5b = 22 Simplify and solve for b: 6b + 5b = 22 11b = 22 b = 2 Now that we have the value of b, we can find the value of a: a = 3b/4 a = 3(2)/4 a = 6/4 a = 3/2 So, the value of a is  3/2. \n#### 3/2'),(' A person is traveling at 20 km/hr and reached his destiny in 2.5 hr then find the distance? ', 'Approach: <using algebra> Using the formula distance = speed × time, we can calculate the distance as follows: Distance = 20 km/hr × 2.5 hr = 50 km So, the closest answer choice is 50 km. \n#### 50'),(' How many keystrokes are needed to type the numbers from 1 to 500? ', 'Approach: <using algebra> Let’s break down the number of keystrokes needed into groups based on the number of digits: One-digit numbers (1-9): There are 9 one-digit numbers, so we need 9 keystrokes. Two-digit numbers (10-99): There are 90 two-digit numbers, each requiring 2 keystrokes, so we need 90 * 2 = 180 keystrokes. Three-digit numbers (100-500): There are 401 three-digit numbers (500 - 100 + 1), each requiring 3 keystrokes, so we need 401 * 3 = 1203 keystrokes. Now let’s add up the keystrokes from all groups: 9 + 180 + 1203 = 1392. \n#### 1392')
]


gsm8k_nshots_pro_refine = [
    (
        'Kylie makes 10 beaded necklaces on Monday and 2 beaded necklaces on Tuesday. Then Kylie makes 5 beaded bracelets on Wednesday. 20 beads are needed to make one beaded necklace. 10 beads are needed to make one beaded bracelet. Ada bought 2000 tomatoes from the grocery store. How many beads does Kylie use in total to make her jewelry?',
        'Kylie requires 240 beads to make beaded necklaces. She also requires 50 beads to make beaded bracelets. How many beads does Kylie use in total to make her jewelry?'
    ),
    (
         'Each bird eats 12 beetles per day, each snake eats 3 birds per day, and each jaguar eats 5 snakes per day. If there are 6 jaguars in a forest, how many beetles are eaten each day?',
         'New Question: In a forest, there are 6 jaguars that each eat 5 snakes per day. Each snake eats 3 birds per day, and each bird eats 12 beetles per day. How many beetles are eaten each day by the jaguars?'
    )
]



def get_answer(res):
    answer = evaluation.extract_ans_from_response(res)
    answer = re.findall(r'-?\d+(?:\.\d+)?(?:/\d+)?', str(answer))[0]
    answer = evaluation.delete_extra_zero(answer)
    return answer

# def read_json(file_path):
#     json_file_path=file_path
#     number=[]
#     with open(json_file_path,'r') as file:
#         for line in file:
#             number=line
#     return number


def read_data(file_path):
    select_data=[0, 1, 2, 6, 9, 10, 14, 17, 18, 19, 20, 22, 25, 26, 27, 28, 31, 33, 34, 37, 39, 40, 44, 46, 47, 48, 49, 50, 51, 54, 56, 57, 59, 60, 61, 62, 63, 67, 68, 70, 71, 73, 75, 78, 80, 82, 83, 86, 87, 88, 91, 92, 93, 95, 96, 97, 98, 102, 103, 104, 105, 106, 107, 108, 111, 112, 115, 117, 118, 121, 122, 124, 126, 128, 129, 130, 132, 135, 137, 138, 139, 140, 141, 142, 144, 145, 146, 147, 148, 149, 153, 154, 156, 157, 162, 163, 166, 168, 171, 172, 173, 176, 177, 178, 179, 181, 185, 186, 187, 188, 189, 191, 193, 194, 195, 196, 197, 201, 202, 204, 206, 207, 208, 211, 212, 213, 217, 218, 220, 222, 223, 224, 227, 231, 232, 234, 235, 238, 239, 240, 241, 243, 245, 246, 248, 249, 252, 255, 257, 258, 260, 262, 264, 268, 269, 272, 275, 278, 279, 282, 283, 284, 285, 286, 287, 290, 291, 293, 294, 295, 298, 301, 304, 305, 306, 307, 308, 309, 311, 313, 314, 315, 316, 317, 318, 319, 320, 321, 325, 328, 329, 331, 332, 334, 335, 336, 337, 338, 339, 340, 343, 344, 346, 347, 349, 351, 352, 354, 355, 357, 359, 360, 364, 367, 368, 369, 371, 372, 374, 377, 378, 379, 380, 381, 384, 385, 386, 388, 390, 391, 392, 395, 396, 397, 401, 403, 405, 408, 412, 416, 417, 418, 422, 423, 427, 429, 430, 431, 433, 434, 435, 436, 439, 440, 443, 444, 445, 447, 448, 450, 451, 453, 454, 455, 457, 458, 462, 465, 467, 470, 471, 472, 477, 479, 482, 483, 485, 486, 489, 491, 494, 495, 496, 499, 500, 501, 502, 503, 505, 506, 508, 509, 510, 511, 513, 515, 516, 518, 519, 520, 522, 523, 524, 525, 527, 528, 529, 530, 531, 533, 534, 536, 537, 538, 539, 541, 542, 545, 547, 548, 549, 550, 551, 552, 553, 554, 557, 559, 560, 561, 562, 563, 564, 565, 567, 568, 569, 570, 571, 573, 574, 575, 576, 577, 578, 579, 581, 583, 585, 588, 589, 590, 595, 596, 599, 600, 601, 602, 604, 605, 606, 611, 612, 613, 617, 618, 619, 620, 621, 622, 626, 630, 631, 633, 635, 636, 637, 638, 640, 641, 642, 644, 645, 648, 649, 650, 651, 652, 653, 655, 656, 657, 660, 661, 662, 663, 665, 668, 670, 671, 672, 673, 674, 675, 676, 677, 678, 679, 681, 685, 686, 688, 690, 691, 692, 693, 694, 697, 698, 700, 701, 702, 703, 704, 705, 707, 709, 710, 714, 716, 718, 720, 721, 722, 723, 725, 726, 727, 729, 730, 732, 734, 735, 738, 742, 743, 744, 745, 746, 749, 750, 751, 753, 754, 756, 759, 761, 762, 764, 765, 766, 768, 770, 771, 772, 773, 774, 777, 778, 780, 781, 782, 783, 784, 785, 786, 787, 789, 790, 791, 793, 794, 796, 799, 804, 805, 810, 813, 814, 815, 816, 817, 820, 822, 823, 824, 825, 826, 827, 829, 831, 832, 834, 835, 837, 839, 840, 841, 843, 844, 846, 851, 852, 853, 854, 856, 857, 858, 859, 860, 862, 864, 866, 867, 868, 869, 870, 871, 875, 879, 880, 881, 882, 884, 887, 889, 891, 893, 897, 898, 901, 903, 904, 905, 909, 910, 911, 912, 913, 914, 915, 916, 917, 919, 920, 924, 926, 927, 928, 929, 931, 932, 935, 936, 937, 938, 940, 941, 942, 945, 946, 948, 949, 950, 951, 952, 954, 955, 956, 957, 958, 959, 962, 964, 965, 968, 969, 971, 973, 975, 976, 977, 978, 979, 980, 983, 984, 986, 988, 989, 990, 991, 994, 998, 999, 1001, 1004, 1005, 1007, 1013, 1014, 1015, 1017, 1018, 1019, 1020, 1022, 1023, 1025, 1026, 1028, 1030, 1032, 1033, 1034, 1035, 1039, 1040, 1041, 1043, 1044, 1045, 1048, 1049, 1050, 1052, 1053, 1054, 1055, 1056, 1057, 1058, 1059, 1060, 1061, 1062, 1063, 1067, 1071, 1073, 1074, 1075, 1077, 1078, 1080, 1081, 1084, 1085, 1086, 1087, 1089, 1090, 1093, 1096, 1097, 1098, 1099, 1103, 1104, 1106, 1108, 1109, 1111, 1112, 1113, 1114, 1116, 1117, 1118, 1120, 1122, 1123, 1125, 1126, 1127, 1128, 1133, 1134, 1139, 1141, 1142, 1143, 1144, 1147, 1149, 1152, 1153, 1156, 1158, 1159, 1161, 1162, 1163, 1166, 1167, 1170, 1172, 1174, 1176, 1177, 1178, 1179, 1180, 1182, 1187, 1188, 1190, 1192, 1194, 1195, 1196, 1197, 1199, 1200, 1202, 1203, 1206, 1207, 1210, 1211, 1212, 1213, 1214, 1215, 1216, 1217, 1223, 1224, 1225, 1226, 1227, 1231, 1232, 1233, 1235, 1238, 1240, 1241, 1242, 1244, 1245, 1246, 1247, 1248, 1249, 1250, 1252, 1253, 1254, 1255, 1256, 1259, 1260, 1262, 1263, 1265, 1270, 1271, 1272, 1274, 1275, 1278, 1279, 1281, 1282, 1284, 1286, 1288, 1291, 1292, 1294, 1295, 1296, 1297, 1298, 1300, 1301, 1302, 1305, 1306, 1307, 1308, 1309, 1310, 1312, 1313, 1314, 1315, 1317, 1318]
    #select_data=[92,93]
    jsonl_file_path =file_path
    i=0
    questions=[]
    answers=[]
    with open(jsonl_file_path, 'r') as file:
        for line in file:
            try:
                if i in select_data:
                    dictionary = json.loads(line)
                    questions.append(dictionary['question'])
                    answers.append(dictionary['answer'])
                i+=1
            except json.JSONDecodeError:
                print("Error decoding JSON:", line)
    return questions,answers


def count_words(sentence):
    return len(re.sub(r'\W+', ' ', sentence).split())

def question_chats(n: int, question: str) -> list[dict[str, str] | dict[str, str] | dict[str, str] | dict[str, str]]:
    def question_prompt(s):
        return f'Question: {s}'
    def refined_prompt(s):
        return f"Refined problem:{s}"
    # chats=[]

    chats = [
        {"role": "system", "content": "Your task is to refine the problem  following principles: (1) conciseness, the problems should not be overly long, ensuring they remain easily understandable; (2) clarity, the prob lems should avoid ambiguous phrasing and instead utilize quantitative representations ((e.g., Arabic numerals) whenever possible; (3) focus: the problems should clearly convey the intended subject matter,"}]

    for (qu, rq) in gsm8k_nshots_pro_refine[:n]:
        chats.append(
            {"role": "user", "content": question_prompt(qu)})
        chats.append(
            {"role": "assistant", "content": refined_prompt(rq)}
        )
    chats.append({"role": "user", "content": question_prompt(question)})

    return chats

def nshot_chats(n: int, question: str,answer:str,feedback:str,type: int) -> dict:
    def question_prompt(s):
        return f'Question: {s}'

    def answer_prompt(s):
        #add use algebra and think like Alan Turing
        return f"Answer:\nLet's think step by step,\n{s}"
# use algebra and think like Alan Turing.
    def feed_back_prompt(s):
        return f"Feedback:{s}"

    def refine_prompt(s):
        return f"Refine:\nPlease generate the improved version of the answer based on the feedback\n{s}"

    chats=[]
    if type==0:
        chats = [
            {"role": "system", "content": "Your task is to solve a series of math word problems by providing the final answer. Use the format #### [value] to highlight your answer. For example, if the answer is 560, you should write #### 560."}
        ]
    elif type==1:
        chats = [
            {"role": "system",
             "content": "Your task is to give a about 100 words feedback to the answer based on the question from three aspects:Accuracy,Clarity ，give an  example of the improved answer based on the previous feedback and use the format #### [value] to highlight your answer at the end of the improved answer. For example, if the answer is 560, you should write #### 560."}
        ]
    elif type==2:
        chats = [
            {"role": "system",
             "content": "Your task is to give a  example of the improved answer based on the previous feedback and use the format #### [value] to highlight your answer at the end of the improved answer. For example, if the answer is 560, you should write #### 560."}
        ]
    gsm8k=gsm8k_nshots
    for q,a in gsm8k[:n]:
        chats.append(
            {"role": "user", "content": question_prompt(q)})
        chats.append(
            {"role": "assistant", "content": answer_prompt(a)})
        # if type==1:
        #     chats.append(
        #         {'role':'assistant',"content":feed_back_prompt(f)}
        #     )
        # if type==2:
        #     chats.append(
        #         {'role': 'assistant', "content": feed_back_prompt(f)}
        #     )
        #     chats.append(
        #         {'role': 'assistant', "content": refine_prompt(r)}
        #    )

    chats.append({"role": "user", "content": question_prompt(question)})
    if type==1:
        chats.append({"role": "assistant", "content": answer_prompt(answer)})
    if type==2:
        chats.append({"role": "assistant", "content": answer_prompt(answer)})
        chats.append(
            {'role': 'assistant', "content": feed_back_prompt(feedback)}
        )
    return chats

# def feedback_chats(n: int, question: str) -> dict:
#     def question_prompt(s):
#         return f'Question: {s}'
#
#     def answer_prompt(s):
#         return f"Answer:\nLet's think step by step.\n{s}"
#
#
#     # chats=[]
#     chats = [
#         {"role": "system", "content": "Your task is to solve a series of math word problems by providing the final answer. Use the format #### [value] to highlight your answer. For example, if the answer is 560, you should write #### 560."}
#     ]
#
#     for q, a in gsm8k_nshots[:n]:
#         chats.append(
#             {"role": "user", "content": question_prompt(q)})
#         chats.append(
#             {"role": "assistant", "content": answer_prompt(a)})
#
#     chats.append({"role": "user", "content": question_prompt(question)})
#     return chats


@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(100))
def zero_pro(message):
    #print('here')
    #print('zero_pro message',message)
    return  client.chat.completions.create(model="Meta-Llama-3.1-8B-Instruct",messages=message,stream= True)
@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(100))
def few_pro(message):
   # print('few_pro message',message)
    return client_1.chat.completions.create(model="Meta-Llama-3.1-8B-Instruct", messages=message, stream=True)


def unzip(temp,completion):
    for chunk in completion:
        ##print('chunk.choices[0].delta.content',chunk.choices[0].delta.content)
        #print('chunk',chunk)
        temp += chunk.choices[0].delta.content + ' '
    return temp



def zero_answer(question,type):
    # problem_refine_prompt=question_chats(2,question)
    # ##print('origin pro',question)
    # completion_prorefine=zero_pro(problem_refine_prompt)
    #
    # zero_pro_temp=''
    # zero_pro_temp=unzip(zero_pro_temp,completion_prorefine)
    zero_pro_temp=question
    ##print('pro_temp',zero_pro_temp)

    zero_shot_prompt = nshot_chats(n=0, question=zero_pro_temp, answer='', feedback='', type=0)
    #print('here')
    completion_zero = zero_pro(zero_shot_prompt)
    zero_temp = ''
    zero_temp = unzip(zero_temp, completion_zero)
    num=count_words(zero_temp)

    if type==1:
        zero_answer = zero_temp
        zero_feedback_prompt = nshot_chats(n=0, question=zero_pro_temp, answer=zero_answer, feedback='', type=1)
        completion_zero_feedback = zero_pro(zero_feedback_prompt)
        zero_feedback_temp = ''

        zero_feedback_temp = unzip(zero_feedback_temp, completion_zero_feedback)
        zero_temp=zero_feedback_temp
    #write data to file
    # json_object = {"question": question, "answer": zero_temp}
    # with open('refine.jsonl', 'a') as file:
    #     json_string = json.dumps(json_object)
    #     file.write(json_string + '\n')
    # print('zero_answer',zero_temp)

    return zero_temp,num

def few_answer(question,type):
    # problem_refine_prompt = question_chats(2, question)
    #
    # completion_prorefine = few_pro(problem_refine_prompt)
    #
    # few_pro_temp = ''
    # few_pro_temp = unzip(few_pro_temp, completion_prorefine)
    few_pro_temp=question

    few_shot_prompt = nshot_chats(n=5, question=few_pro_temp, answer='', feedback='', type=0)
    completion_few = few_pro(few_shot_prompt)
    few_temp = ''
    few_temp = unzip(few_temp, completion_few)

    ini_answer=few_temp
    time_num=count_words(ini_answer)
    if type==1:
        few_answer = few_temp
        few_feedback_prompt = nshot_chats(n=0, question=few_pro_temp, answer=few_answer, feedback='', type=1)
        completion_few_feedback = few_pro(few_feedback_prompt)
        few_feedback_temp = ''
        few_feedback_temp = unzip(few_feedback_temp, completion_few_feedback)
        few_temp=few_feedback_temp
    # write data to file
    json_object={"question":question,'answer':few_temp}
    with open('5_shorts.jsonl', 'a') as file:
        json_string = json.dumps(json_object)
        file.write(json_string + '\n')
    #print('few_answer',few_temp)
    return few_temp,time_num

def few_answer_copy(question,type):
    # problem_refine_prompt = question_chats(2, question)
    #
    # completion_prorefine = few_pro(problem_refine_prompt)
    #
    # few_pro_temp = ''
    # few_pro_temp = unzip(few_pro_temp, completion_prorefine)
    few_pro_temp=question

    few_shot_prompt = nshot_chats(n=5, question=few_pro_temp, answer='', feedback='', type=0)
    completion_few = zero_pro(few_shot_prompt)
    few_temp = ''
    few_temp = unzip(few_temp, completion_few)

    ini_answer=few_temp
    time_num=count_words(ini_answer)
    if type==1:
        few_answer = few_temp
        few_feedback_prompt = nshot_chats(n=0, question=few_pro_temp, answer=few_answer, feedback='', type=1)
        completion_few_feedback = zero_pro(few_feedback_prompt)
        few_feedback_temp = ''
        few_feedback_temp = unzip(few_feedback_temp, completion_few_feedback)
        few_temp=few_feedback_temp
    # write data to file
    json_object={"question":question,'answer':few_temp}
    with open('5_shorts.jsonl', 'a') as file:
        json_string = json.dumps(json_object)
        file.write(json_string + '\n')
    #print('few_answer',few_temp)
    return few_temp,time_num


def train(type):
    #numbers=read_json('indices_800.json')
    #print('numbers',numbers)
    questions,answers=read_data('test.jsonl')
    #print(questions[1])
    res_zero=[]
    res_few=[]
    i=1
    # baseline and refine and repolish
    part_q=questions
    # print('item',len(questions))
    #print('part_q',part_q)
    part_a=answers
    # print('part_a',part_a)

    count_num=0
    for question in part_q: #baseline\refine\repolish
    #for number in numbers:
       # print(number)
       # question=questions[number]['question']
        print('question',question)
        print('i',i)
        #z_answer,z_num=zero_answer(question,type)
        z_answer, z_num = zero_answer(question, type)
        count_num+=z_num
        res_zero.append(z_answer)

        f_answer,f_num=few_answer(question,type)
        #count_num+=f_num

        res_few.append(f_answer)
        # if i%10==0:
        #     #print('sleep')
        #     time.sleep(8)
        i+=1
    print('res_zero',res_zero)
    print('res_few',res_few)
    num=int(count_num/i)
    return part_a,res_zero,res_few,num

