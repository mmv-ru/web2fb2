<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:fb="http://www.gribuser.ru/xml/fictionbook/2.0"  xmlns="http://www.w3.org/1999/xhtml">
	<xsl:output method="xml" encoding="UTF-8"/>
	
	<xsl:template match="/*">
		<html>
			<head>
				<title>
					<xsl:value-of select="fb:description/fb:title-info/fb:book-title"/>
				</title>
				<link href="style.css" type="text/css" charset="UTF-8" rel="stylesheet"/>
			</head>
			<body>
				<!-- BUILD BOOK -->
				<xsl:for-each select="fb:body">
					<!-- <xsl:apply-templates /> -->
					<xsl:apply-templates/>
				</xsl:for-each>
			</body>
		</html>
	</xsl:template>
	
	
	<!-- body -->
	<xsl:template match="fb:body">
		<div><xsl:apply-templates/></div>
	</xsl:template>

	<xsl:template match="fb:section">
		<xsl:apply-templates/>
	</xsl:template>
	
	
	<!-- section/title -->
	<xsl:template match="fb:section/fb:title|fb:poem/fb:title">
		<xsl:choose>
			<xsl:when test="count(ancestor::node()) &lt; 9">
				<xsl:element name="{concat('h',count(ancestor::node())-3)}">
					<xsl:apply-templates/>
				</xsl:element>
			</xsl:when>
			<xsl:otherwise>
				<xsl:element name="h6">
					
					<xsl:apply-templates/>
				</xsl:element>
			</xsl:otherwise>
		</xsl:choose>
	</xsl:template>
	<!-- section/title -->
	<xsl:template match="fb:body/fb:title">
		<h1><xsl:apply-templates mode="title"/></h1>
	</xsl:template>

	<xsl:template match="fb:title/fb:p">
		<xsl:apply-templates/><xsl:text disable-output-escaping="no">&#032;</xsl:text><br/>
	</xsl:template>
	<!-- subtitle -->
	<xsl:template match="fb:subtitle">
		<h5>
			<xsl:apply-templates/>
		</h5>
	</xsl:template>
	
	<!-- p -->
	<xsl:template match="fb:p">
		<div>	&#160;&#160;&#160;<xsl:apply-templates/></div>
	</xsl:template>
	
	<!-- code -->
	<xsl:template match="fb:code">
		<pre><xsl:apply-templates/></pre>
	</xsl:template>
	
	<!-- strong -->
	<xsl:template match="fb:strong">
		<b><xsl:apply-templates/></b>
	</xsl:template>
	
	<!-- emphasis -->
	<xsl:template match="fb:emphasis">
		<i>	<xsl:apply-templates/></i>
	</xsl:template>
	
	<!-- style -->
	<xsl:template match="fb:style">
		<span class="{@name}"><xsl:apply-templates/></span>
	</xsl:template>
	
	<!-- empty-line -->
	<xsl:template match="fb:empty-line">
		<br/>
	</xsl:template>
	
	<!-- link -->
	<xsl:template match="fb:a">
		<xsl:element name="a">
			<xsl:attribute name="href"><xsl:value-of select="@xlink:href"/></xsl:attribute>
			<xsl:attribute name="title">
				<xsl:choose>
					<xsl:when test="starts-with(@xlink:href,'#')"><xsl:value-of select="key('note-link',substring-after(@xlink:href,'#'))/fb:p"/></xsl:when>
					<xsl:otherwise><xsl:value-of select="key('note-link',@xlink:href)/fb:p"/></xsl:otherwise>
				</xsl:choose>
			</xsl:attribute>
			<xsl:choose>
				<xsl:when test="(@type) = 'note'">
					<sup>
						<xsl:apply-templates/>
					</sup>
				</xsl:when>
				<xsl:otherwise>
					<xsl:apply-templates/>
				</xsl:otherwise>
			</xsl:choose>
		</xsl:element>
	</xsl:template>
	<!-- annotation -->
	<xsl:template name="annotation">
		<h3>Annotation</h3>
		<xsl:apply-templates/>
	</xsl:template>
	<!-- epigraph -->
	<xsl:template match="fb:epigraph">
		<blockquote class="epigraph">
			<xsl:apply-templates/>
		</blockquote>
	</xsl:template>
	<!-- epigraph/text-author -->
	<xsl:template match="fb:epigraph/fb:text-author">
		<blockquote>
			<i><xsl:apply-templates/></i>
		</blockquote>
	</xsl:template>
	<!-- cite -->
	<xsl:template match="fb:cite">
		<blockquote>
		<xsl:apply-templates/>
		</blockquote>
	</xsl:template>
	<!-- cite/text-author -->
	<xsl:template match="fb:text-author">
		<blockquote>
		<i>	<xsl:apply-templates/></i></blockquote>
	</xsl:template>
	<!-- date -->
	<xsl:template match="fb:date">
		<xsl:choose>
			<xsl:when test="not(@value)">
				&#160;&#160;&#160;<xsl:apply-templates/>
				<br/>
			</xsl:when>
			<xsl:otherwise>
				&#160;&#160;&#160;<xsl:value-of select="@value"/>
				<br/>
			</xsl:otherwise>
		</xsl:choose>
	</xsl:template>
	<!-- poem -->
	<xsl:template match="fb:poem">
		<blockquote>
			<xsl:apply-templates/>
		</blockquote>
	</xsl:template>

	<!-- stanza -->
	<xsl:template match="fb:stanza">
		<xsl:apply-templates/>
		<br/>
	</xsl:template>
	<!-- v -->
	<xsl:template match="fb:v">
		<xsl:apply-templates/><br/>
	</xsl:template>
	
	<!-- image - inline -->
	<xsl:template match="fb:p/fb:image|fb:v/fb:image|fb:td/fb:image|fb:subtitle/fb:image">
		<img alt="">
			<xsl:choose>
				<xsl:when test="starts-with(@xlink:href,'#')">
					<xsl:attribute name="src"><xsl:value-of select="substring-after(@xlink:href,'#')"/></xsl:attribute>
				</xsl:when>
				<xsl:otherwise>
					<xsl:attribute name="src"><xsl:value-of select="@xlink:href"/></xsl:attribute>
				</xsl:otherwise>
			</xsl:choose>
		</img>
	</xsl:template>
	
	<!-- image -->
	<xsl:template match="fb:image">
		<div class = "img">
			<img alt="">
				<xsl:choose>
					<xsl:when test="starts-with(@xlink:href,'#')">
						<xsl:attribute name="src"><xsl:value-of select="substring-after(@xlink:href,'#')"/></xsl:attribute>
					</xsl:when>
					<xsl:otherwise>
						<xsl:attribute name="src"><xsl:value-of select="@xlink:href"/></xsl:attribute>
					</xsl:otherwise>
				</xsl:choose>
			</img>
		</div>
	</xsl:template>
	
	<!-- strikethrough-sub-sup -->
	<xsl:template match="fb:sup">
		<sup>
			<xsl:apply-templates/>			
		</sup>
	</xsl:template>
	<xsl:template match="fb:sub">
		<sub>
			<xsl:apply-templates/>			
		</sub>
	</xsl:template>
	
	<!--Table-->
	<xsl:template match="fb:table">
		<table border = "1">
			<xsl:apply-templates/>
		</table>
	</xsl:template>
	<xsl:template match="fb:tr">
		<tr>
			<xsl:apply-templates/>
		</tr>
	</xsl:template>
	<xsl:template match="fb:td|fb:th">
		<xsl:element name="{name()}">
			<xsl:for-each select="@*">
				<xsl:attribute name="{name()}">
					<xsl:value-of select="."/>
				</xsl:attribute>	
			</xsl:for-each>
			<xsl:apply-templates/>			
		</xsl:element>
	</xsl:template>
	
</xsl:stylesheet>
